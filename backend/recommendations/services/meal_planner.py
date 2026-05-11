import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass
from recipes.models import Recipe
from profiles.models import Profile
from recipes.serializers import SingleRecipeSerializer
from ..models import MealType
from .recipe_matcher import RecipeMatcher
from .recommender_engine import RecommenderEngine


@dataclass
class MealPlan:
    """Represents a daily meal plan"""
    breakfast: Optional[Recipe] = None
    lunch: Optional[Recipe] = None
    dinner: Optional[Recipe] = None
    snack: Optional[Recipe] = None

    # Totals
    total_calories: float = 0.0
    total_protein: float = 0.0
    total_carbohydrate: float = 0.0
    total_fat: float = 0.0
    total_fiber: float = 0.0

    def calculate_totals(self):
        """Sums up nutritional values from all meals"""
        self.total_calories = 0
        self.total_protein = 0
        self.total_carbohydrate = 0
        self.total_fat = 0
        self.total_fiber = 0

        meals = [self.breakfast, self.lunch, self.dinner, self.snack]

        for recipe in filter(None, meals):
            self.total_calories += float(recipe.calories or 0)
            self.total_protein += float(recipe.protein or 0)
            self.total_carbohydrate += float(recipe.carbohydrate or 0)
            self.total_fat += float(recipe.fat or 0)
            self.total_fiber += float(recipe.fiber or 0)

    def get_deviation_from_target(self, profile: Profile) -> Dict[str, float]:
        """Calculate percentage deviation from target macros"""
        if not profile.daily_calories:
            return {}

        def calc_dev(actual, target):
            target = float(target or 1)
            return ((actual - target) / target) * 100

        return {
            'calories': calc_dev(self.total_calories, profile.daily_calories),
            'protein': calc_dev(self.total_protein, profile.daily_protein),
            'carbohydrate': calc_dev(self.total_carbohydrate, profile.daily_carbohydrates),
            'fat': calc_dev(self.total_fat, profile.daily_fat),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert meal plan to JSON-ready format"""
        return {
            'breakfast': SingleRecipeSerializer(self.breakfast).data if self.breakfast else None,
            'lunch': SingleRecipeSerializer(self.lunch).data if self.lunch else None,
            'dinner': SingleRecipeSerializer(self.dinner).data if self.dinner else None,
            'snack': SingleRecipeSerializer(self.snack).data if self.snack else None,  # <--- NOWE
            'totals': {
                'calories': round(self.total_calories, 1),
                'protein': round(self.total_protein, 1),
                'carbohydrate': round(self.total_carbohydrate, 1),
                'fat': round(self.total_fat, 1),
                'fiber': round(self.total_fiber, 1),
            }
        }


class MealPlanner:
    """Service for generating complete daily meal plans"""

    def __init__(self):
        self.matcher = RecommenderEngine()

    def create_meal_plan(self, profile: Profile, date: Optional[datetime.date] = None) -> Optional[MealPlan]:
        today = date or datetime.date.today()
        plan = MealPlan()
        planned: list[Recipe] = []

        plan.breakfast = self.matcher.find_best_recipe(
            profile, MealType.BREAKFAST, date=today, already_planned=planned, try_relaxed=True
        )
        if plan.breakfast:
            planned.append(plan.breakfast)

        plan.lunch = self.matcher.find_best_recipe(
            profile, MealType.LUNCH, date=today, already_planned=planned, try_relaxed=True
        )
        if plan.lunch:
            planned.append(plan.lunch)

        plan.dinner = self.matcher.find_best_recipe(
            profile, MealType.DINNER, date=today, already_planned=planned, try_relaxed=True
        )
        if plan.dinner:
            planned.append(plan.dinner)

        plan.snack = self.matcher.find_best_recipe(
            profile, MealType.SNACK, date=today, already_planned=planned, try_relaxed=True
        )

        if not (plan.breakfast and plan.lunch and plan.dinner and plan.snack):
            return None

        plan.calculate_totals()

        return plan

