import math
import datetime
from typing import Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from profiles.models import Profile
from recipes.models import Recipe
from .constraint_manager import MEAL_DISTRIBUTIONS
from .user_context import UserContext

# Per-goal macro weights used in S_macro
_GOAL_WEIGHTS = {
    Profile.NutritionalGoal.LOSE_WEIGHT:     {'protein': 2.5, 'carbs': 0.8, 'fat': 1.0},
    Profile.NutritionalGoal.GAIN_WEIGHT:     {'protein': 2.0, 'carbs': 1.5, 'fat': 1.0},
    Profile.NutritionalGoal.MAINTAIN_WEIGHT: {'protein': 2.0, 'carbs': 1.0, 'fat': 1.0},
}
_DEFAULT_WEIGHTS = {'protein': 2.0, 'carbs': 1.0, 'fat': 1.0}

# Composite score weights (must sum to 1.0)
W_MACRO = 0.50
W_PREF = 0.35
W_DIV = 0.15

# Preference score threshold: only recipes rated >= this influence the taste centroid
LIKED_THRESHOLD = 4

# Recency decay half-life in days (score reaches ~0.63 after this many days)
RECENCY_HALF_LIFE = 3.0


class RecipeScorer:
    """
    Computes a composite [0, 1] score for a recipe given user context.

    final = W_MACRO * S_macro + W_PREF * S_pref + W_DIV * S_div
    """

    def __init__(self, feature_cache: Optional[dict] = None):
        self._feature_cache = feature_cache  # recipe_id → np.ndarray; None = skip S_pref

    # ── Public API ────────────────────────────────────────────────────────────

    def score(
        self,
        recipe: Recipe,
        profile: Profile,
        meal_type: str,
        context: UserContext,
        already_planned: list,
        reference_date: Optional[datetime.date] = None,
    ) -> float:
        s_macro = self.macro_score(recipe, profile, meal_type)
        s_pref = self.preference_score(recipe, context)
        s_div = self.diversity_score(recipe, context, already_planned, reference_date)
        return W_MACRO * s_macro + W_PREF * s_pref + W_DIV * s_div

    # ── S_macro ───────────────────────────────────────────────────────────────

    def macro_score(self, recipe: Recipe, profile: Profile, meal_type: str) -> float:
        """Weighted closeness to per-meal macro targets, adapted to nutritional goal. → [0, 1]"""
        targets = self._target_macros(profile, meal_type)
        weights = _GOAL_WEIGHTS.get(profile.nutritional_goal, _DEFAULT_WEIGHTS)
        weight_sum = sum(weights.values())

        weighted_score = 0.0
        for macro, weight in weights.items():
            target = targets[macro] or 1.0
            field = 'carbohydrate' if macro == 'carbs' else macro
            actual = float(getattr(recipe, field) or 0)
            pct_off = abs(actual - target) / target
            raw = max(0.0, 1.0 - pct_off)
            weighted_score += raw * weight

        return weighted_score / weight_sum

    # ── S_pref ────────────────────────────────────────────────────────────────

    def preference_score(self, recipe: Recipe, context: UserContext) -> float:
        """Cosine similarity between candidate and the user's rating-weighted taste centroid. → [0, 1]"""
        if self._feature_cache is None:
            return 0.5  # no feature matrix available

        candidate_vec = self._feature_cache.get(recipe.id)
        if candidate_vec is None:
            return 0.5

        liked_ids = [rid for rid, rating in context.ratings.items() if rating >= LIKED_THRESHOLD]
        liked_vecs = [self._feature_cache[rid] for rid in liked_ids if rid in self._feature_cache]

        if not liked_vecs:
            return 0.5  # cold start — neutral score

        weights = np.array(
            [context.ratings[rid] / 5.0 for rid in liked_ids if rid in self._feature_cache],
            dtype=np.float32,
        )
        taste_centroid = np.average(liked_vecs, axis=0, weights=weights)

        sim = cosine_similarity(
            candidate_vec.reshape(1, -1),
            taste_centroid.reshape(1, -1),
        )[0][0]
        return float(np.clip(sim, 0.0, 1.0))

    # ── S_div ─────────────────────────────────────────────────────────────────

    def diversity_score(
        self,
        recipe: Recipe,
        context: UserContext,
        already_planned: list,
        reference_date: Optional[datetime.date] = None,
    ) -> float:
        """Recency-decay freshness score penalised by intra-day ingredient overlap. → [0, 1]"""
        days_ago = context.days_since_eaten(recipe.id, reference_date)
        # Exponential approach to 1.0 as days_ago grows
        recency = 1.0 - math.exp(-days_ago / RECENCY_HALF_LIFE)

        if not already_planned:
            return recency

        overlap = _ingredient_overlap(recipe, already_planned)
        # Up to 50% penalty when ingredients fully overlap
        return recency * (1.0 - 0.5 * overlap)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _target_macros(profile: Profile, meal_type: str) -> dict:
        dist = MEAL_DISTRIBUTIONS.get(meal_type, 0.30)
        return {
            'calories': float(profile.daily_calories or 2000) * dist,
            'protein':  float(profile.daily_protein or 150) * dist,
            'carbs':    float(profile.daily_carbohydrates or 250) * dist,
            'fat':      float(profile.daily_fat or 70) * dist,
        }


def _ingredient_set(recipe: Recipe) -> set:
    """Return the canonical ingredient names for a recipe.

    Uses Django's prefetch cache when available (i.e. when the recipe was
    fetched with prefetch_related('structured_ingredients__ingredient')),
    avoiding a per-recipe DB round-trip.  Falls back to a live query otherwise.
    """
    return {
        ri.ingredient.canonical_name
        for ri in recipe.structured_ingredients.all()
        if ri.ingredient_id and ri.ingredient.canonical_name
    }


def _ingredient_overlap(recipe: Recipe, planned: list) -> float:
    """Jaccard similarity of canonical ingredient sets. → [0, 1]"""
    candidate_set = _ingredient_set(recipe)
    if not candidate_set:
        return 0.0

    max_jaccard = 0.0
    for planned_recipe in planned:
        if planned_recipe is None:
            continue
        planned_set = _ingredient_set(planned_recipe)
        union = candidate_set | planned_set
        if not union:
            continue
        jaccard = len(candidate_set & planned_set) / len(union)
        if jaccard > max_jaccard:
            max_jaccard = jaccard

    return max_jaccard
