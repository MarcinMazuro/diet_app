import datetime
from dataclasses import dataclass, field
from typing import Optional

from profiles.models import Profile
from recipes.models import Recipe


@dataclass
class UserContext:
    profile: Profile
    # recipe_id → rating value (1-5)
    ratings: dict = field(default_factory=dict)
    # recipe_id → most recent date eaten
    meal_history: dict = field(default_factory=dict)
    # recipes already assigned for the current session (intra-day diversity)
    planned_today: list = field(default_factory=list)

    @classmethod
    def from_profile(cls, profile: Profile, reference_date: datetime.date) -> 'UserContext':
        from recommendations.models import Meal, Rating

        ratings = dict(
            Rating.objects.filter(profile=profile)
            .values_list('recipe_id', 'rating')
        )

        # Most recent date per recipe eaten in the past 30 days
        cutoff = reference_date - datetime.timedelta(days=30)
        meal_history: dict[int, datetime.date] = {}
        for recipe_id, eaten_date in (
            Meal.objects.filter(profile=profile, date__gte=cutoff)
            .values_list('recipe_id', 'date')
            .order_by('date')
        ):
            meal_history[recipe_id] = eaten_date  # later dates overwrite earlier ones

        return cls(profile=profile, ratings=ratings, meal_history=meal_history)

    def days_since_eaten(self, recipe_id: int, reference_date: Optional[datetime.date] = None) -> int:
        """Returns days since the recipe was last eaten, or a large number if never."""
        if recipe_id not in self.meal_history:
            return 999
        last_eaten = self.meal_history[recipe_id]
        today = reference_date or datetime.date.today()
        return (today - last_eaten).days
