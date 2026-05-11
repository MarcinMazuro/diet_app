import datetime
import logging
from typing import Optional

from profiles.models import Profile
from recipes.models import Recipe
from recommendations.models import MealType

from .constraint_manager import ConstraintManager
from .diversity_layer import DiversityLayer
from .feature_builder import build_matrix
from .recipe_scorer import RecipeScorer
from .user_context import UserContext

logger = logging.getLogger(__name__)

# Number of top candidates passed to DiversityLayer for re-ranking
TOP_N = 10


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

        # ── Stage 0: UserContext ──────────────────────────────────────────────
        context = UserContext.from_profile(profile, reference_date)

        # ── Stage 1: Hard filtering ───────────────────────────────────────────
        candidates = self._get_candidates(profile, meal_type, reference_date, try_relaxed)
        if not candidates:
            logger.debug(
                "RecommenderEngine: no candidates for %s / %s on %s",
                profile.id, meal_type, reference_date,
            )
            return None

        # ── Stage 2: Multi-factor scoring ─────────────────────────────────────
        feature_cache = self._get_feature_cache()
        scorer = RecipeScorer(feature_cache=feature_cache)

        scored = [
            (recipe, scorer.score(recipe, profile, meal_type, context, already_planned, reference_date))
            for recipe in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored[:TOP_N]

        # ── Stage 3: Diversity re-rank ────────────────────────────────────────
        best = self._diversity.rerank_for_day(top_candidates, already_planned)

        logger.debug(
            "RecommenderEngine: selected recipe %s (id=%s) for %s / %s",
            best.name, best.id, profile.id, meal_type,
        )
        return best

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_candidates(
        self,
        profile: Profile,
        meal_type: str,
        reference_date: datetime.date,
        try_relaxed: bool,
    ) -> list:
        candidates = list(
            self._constraints.apply(profile, meal_type, reference_date, try_relaxed=False)
            .prefetch_related('structured_ingredients__ingredient')
        )

        if not candidates and try_relaxed:
            candidates = list(
                self._constraints.apply(profile, meal_type, reference_date, try_relaxed=True)
                .prefetch_related('structured_ingredients__ingredient')
            )

        if not candidates and self._constraints.recency_window_days > 0:
            relaxed_mgr = ConstraintManager(recency_window_days=0)
            candidates = list(
                relaxed_mgr.apply(profile, meal_type, reference_date, try_relaxed=True)
                .prefetch_related('structured_ingredients__ingredient')
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
