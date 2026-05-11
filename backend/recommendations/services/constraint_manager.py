import datetime
from typing import Optional

from recipes.models import Recipe
from profiles.models import Profile
from recommendations.models import MealType

MEAL_TYPE_MAPPING = {
    MealType.BREAKFAST: ['breakfast', 'brunch', 'afternoon tea'],
    MealType.LUNCH: ['lunch', 'picnic', 'soup', 'salad', 'starter', 'side dish'],
    MealType.DINNER: ['dinner', 'supper', 'main course', 'fish course'],
    MealType.SNACK: ['snack', 'treat', 'canapes', 'dessert'],
}

MEAL_DISTRIBUTIONS = {
    MealType.BREAKFAST: 0.25,
    MealType.LUNCH: 0.35,
    MealType.DINNER: 0.30,
    MealType.SNACK: 0.10,
}


class ConstraintManager:
    """Hard constraint filtering — zero-tolerance exclusions applied before scoring."""

    DISLIKE_THRESHOLD = 2  # exclude recipes rated at or below this

    def __init__(self, recency_window_days: int = 5):
        self.recency_window_days = recency_window_days

    def apply(
        self,
        profile: Profile,
        meal_type: str,
        reference_date: datetime.date,
        try_relaxed: bool = False,
    ):
        """
        Returns a QuerySet of Recipe candidates that pass all hard constraints.
        Calorie filtering is strict (±15%) by default; pass try_relaxed=True
        to widen to ±30% (used as fallback when strict yields nothing).
        """
        from recommendations.models import Meal, Rating

        queryset = Recipe.objects.all()

        # 1. Dietary preference filter
        if hasattr(profile, 'diet') and profile.diet:
            queryset = queryset.filter(categories__name__iexact=profile.diet)

        # 2. Meal-type category filter
        valid_tags = MEAL_TYPE_MAPPING.get(meal_type, [])
        if valid_tags:
            queryset = queryset.filter(categories__name__in=valid_tags)

        # 3. Recency exclusion
        if self.recency_window_days > 0:
            cutoff = reference_date - datetime.timedelta(days=self.recency_window_days)
            recent_ids = Meal.objects.filter(
                profile=profile,
                date__gte=cutoff,
            ).values_list('recipe_id', flat=True)
            queryset = queryset.exclude(id__in=recent_ids)

        # 4. Dislike exclusion
        disliked_ids = Rating.objects.filter(
            profile=profile,
            rating__lte=self.DISLIKE_THRESHOLD,
        ).values_list('recipe_id', flat=True)
        queryset = queryset.exclude(id__in=disliked_ids)

        # 5. Calorie range filter
        queryset = self._apply_calorie_filter(queryset, profile, meal_type, relaxed=try_relaxed)

        return queryset.distinct()

    def _apply_calorie_filter(self, queryset, profile: Profile, meal_type: str, relaxed: bool = False):
        if not profile.daily_calories:
            return queryset

        dist = MEAL_DISTRIBUTIONS.get(meal_type, 0.30)
        target_cal = float(profile.daily_calories) * dist
        margin = 0.30 if relaxed else 0.15

        return queryset.filter(
            calories__gte=target_cal * (1 - margin),
            calories__lte=target_cal * (1 + margin),
        )
