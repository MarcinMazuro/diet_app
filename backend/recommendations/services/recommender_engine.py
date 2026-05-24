import datetime
import logging
from typing import Optional

from django.db.models import prefetch_related_objects

from profiles.models import Profile
from recipes.models import Recipe
from recommendations.models import MealType

from .constraint_manager import ConstraintManager
from .diversity_layer import DiversityLayer
from .feature_builder import build_matrix
from .recipe_scorer import RecipeScorer, W_MACRO, W_PREF, W_DIV
from .user_context import UserContext

logger = logging.getLogger(__name__)

# Candidates sent to the diversity re-ranker
TOP_N = 10
# Extra buffer for two-pass scoring (ensures top-10 is stable after S_div is added)
TOP_N_PREFETCH = TOP_N * 2


class RecommenderEngine:
    """
    Drop-in replacement for RecipeMatcher.

    find_best_recipe() has the same return type (Optional[Recipe]) and the same
    keyword arguments so MealPlanner requires only a one-line constructor change.

    Pipeline
    --------
    Stage 0 — UserContext: load profile signals (ratings, meal history).
    Stage 1 — ConstraintManager: hard filter (dietary, recency, dislikes, calories).
    Stage 2 — RecipeScorer: multi-factor score (macro fit + preference + diversity).
    Stage 3 — DiversityLayer: intra-day re-rank on ingredient overlap.
    """

    def __init__(self):
        self._constraints = ConstraintManager()
        self._diversity = DiversityLayer()
        # Feature matrix is built lazily on first recommendation request.
        self._feature_cache: Optional[dict] = None
        # UserContext cache: (profile_id, date) → UserContext
        # Avoids re-querying ratings + meal history for each slot in a daily plan.
        self._context_cache: dict = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def find_best_recipe(
        self,
        profile: Profile,
        meal_type: str = MealType.BREAKFAST,
        date: Optional[datetime.date] = None,
        already_planned: Optional[list] = None,
        try_relaxed: bool = True,
    ) -> Optional[Recipe]:
        """Return the best recipe for the given profile and meal slot."""
        if not profile.daily_calories:
            return None

        reference_date = date or datetime.date.today()
        already_planned = already_planned or []

        # ── Stage 0: UserContext (cached per profile+date within this engine) ──
        context = self._get_context(profile, reference_date)

        # ── Stage 1: Hard filtering ───────────────────────────────────────────
        candidates = self._get_candidates(profile, meal_type, reference_date, try_relaxed)
        if not candidates:
            logger.debug(
                "RecommenderEngine: no candidates for %s / %s on %s",
                profile.id, meal_type, reference_date,
            )
            return None

        # ── Stage 2: Two-pass multi-factor scoring ────────────────────────────
        feature_cache = self._get_feature_cache()
        scorer = RecipeScorer(feature_cache=feature_cache)

        # Pass 1: rank all candidates by macro + preference (no DB queries needed)
        partial_scored = [
            (r, scorer.macro_score(r, profile, meal_type) * W_MACRO
               + scorer.preference_score(r, context) * W_PREF)
            for r in candidates
        ]
        partial_scored.sort(key=lambda x: x[1], reverse=True)
        top_recipes = [r for r, _ in partial_scored[:TOP_N_PREFETCH]]

        # Prefetch ingredients only for the finalists + already-planned meals.
        # S_div ingredient overlap is only non-zero when already_planned is non-empty.
        if already_planned:
            prefetch_related_objects(
                top_recipes + [r for r in already_planned if r is not None],
                'structured_ingredients__ingredient',
            )

        # Pass 2: add S_div, re-sort, pick top-N for the diversity layer
        top_scored = [
            (r, partial + scorer.diversity_score(r, context, already_planned, reference_date) * W_DIV)
            for r, partial in partial_scored[:TOP_N_PREFETCH]
        ]
        top_scored.sort(key=lambda x: x[1], reverse=True)
        top_candidates = top_scored[:TOP_N]

        # ── Stage 3: Diversity re-rank ────────────────────────────────────────
        best = self._diversity.rerank_for_day(top_candidates, already_planned)

        logger.debug(
            "RecommenderEngine: selected recipe %s (id=%s) for %s / %s",
            best.name, best.id, profile.id, meal_type,
        )
        return best

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_context(self, profile: Profile, reference_date: datetime.date) -> UserContext:
        """Return cached UserContext for this profile+date, building it on first call."""
        key = (profile.id, reference_date)
        if key not in self._context_cache:
            self._context_cache[key] = UserContext.from_profile(profile, reference_date)
        return self._context_cache[key]

    def _get_candidates(
        self,
        profile: Profile,
        meal_type: str,
        reference_date: datetime.date,
        try_relaxed: bool,
    ) -> list:
        candidates = list(
            self._constraints.apply(profile, meal_type, reference_date, try_relaxed=False)
        )

        if not candidates and try_relaxed:
            candidates = list(
                self._constraints.apply(profile, meal_type, reference_date, try_relaxed=True)
            )

        if not candidates and self._constraints.recency_window_days > 0:
            relaxed_mgr = ConstraintManager(recency_window_days=0)
            candidates = list(
                relaxed_mgr.apply(profile, meal_type, reference_date, try_relaxed=True)
            )

        return candidates

    def _get_feature_cache(self) -> dict:
        if self._feature_cache is None:
            try:
                self._feature_cache = build_matrix()
            except Exception as exc:
                logger.warning("RecommenderEngine: feature matrix build failed (%s). Falling back.", exc)
                self._feature_cache = {}
        return self._feature_cache
