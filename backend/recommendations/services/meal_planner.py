from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from recipes.models import Recipe
from profiles.models import Profile
from recipes.serializers import RecipeSerializer
from ..models import Recommendation
from .recipe_matcher import RecipeMatcher


@dataclass
class MealPlan:
    """Represents a daily meal plan"""
    breakfast: Optional[Recipe] = None
    lunch: Optional[Recipe] = None
    dinner: Optional[Recipe] = None
    snack: Optional[Recipe] = None  # <--- NOWE POLE

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
            'breakfast': RecipeSerializer(self.breakfast).data if self.breakfast else None,
            'lunch': RecipeSerializer(self.lunch).data if self.lunch else None,
            'dinner': RecipeSerializer(self.dinner).data if self.dinner else None,
            'snack': RecipeSerializer(self.snack).data if self.snack else None,  # <--- NOWE
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
        self.matcher = RecipeMatcher()

    def create_meal_plan(self, profile: Profile) -> Optional[MealPlan]:
        plan = MealPlan()

        plan.breakfast = self.matcher.find_best_recipe(profile, 'BREAKFAST', try_relaxed=True)
        plan.lunch = self.matcher.find_best_recipe(profile, 'LUNCH', try_relaxed=True)
        plan.dinner = self.matcher.find_best_recipe(profile, 'DINNER', try_relaxed=True)
        plan.snack = self.matcher.find_best_recipe(profile, 'SNACK', try_relaxed=True)  # <--- NOWE

        if not (plan.breakfast and plan.lunch and plan.dinner and plan.snack):
            return None

        plan.calculate_totals()

        return plan

    def save_meal_plan(self, plan: MealPlan, profile: Profile) -> None:
        """Save meal plan recommendations to database history"""
        meals = [
            ('BREAKFAST', plan.breakfast),
            ('LUNCH', plan.lunch),
            ('DINNER', plan.dinner),
            ('SNACK', plan.snack)  # <--- NOWE
        ]

        for meal_type, recipe in meals:
            if recipe:
                Recommendation.objects.create(
                    profile=profile,
                    recipe=recipe,
                )