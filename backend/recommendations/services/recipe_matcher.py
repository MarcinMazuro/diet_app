import random
from typing import Optional
from recipes.models import Recipe
from profiles.models import Profile


class RecipeMatcher:
    MEAL_DISTRIBUTIONS = {
        'BREAKFAST': 0.25,
        'LUNCH': 0.35,
        'DINNER': 0.30,
        'SNACK': 0.10
    }

    MEAL_TYPE_MAPPING = {
        'BREAKFAST': ['breakfast', 'brunch', 'afternoon tea'],
        'LUNCH': ['lunch', 'picnic', 'soup', 'salad', 'starter', 'side dish'],
        'DINNER': ['dinner', 'supper', 'main course', 'fish course'],
        'SNACK': ['snack', 'treat', 'canapes', 'dessert']
    }

    def find_best_recipe(
            self,
            profile: Profile,
            meal_type: str = 'BREAKFAST',
            try_relaxed: bool = True
    ) -> Optional[Recipe]:
        """Return the best matching recipe for the given profile and meal type"""

        if not profile.daily_calories:
            return None

        queryset = Recipe.objects.all()

        if hasattr(profile, 'diet') and profile.diet:
            queryset = queryset.filter(categories__name__iexact=profile.diet)

        valid_tags = self.MEAL_TYPE_MAPPING.get(meal_type, [])
        if valid_tags:
            queryset = queryset.filter(categories__name__in=valid_tags)

        target_macros = self._calculate_target_macros(profile, meal_type)
        target_cal = target_macros['calories']

        candidates = list(queryset.filter(
            calories__gte=target_cal * 0.85,
            calories__lte=target_cal * 1.15
        ).distinct())

        if not candidates and try_relaxed:
            candidates = list(queryset.filter(
                calories__gte=target_cal * 0.70,
                calories__lte=target_cal * 1.30
            ).distinct())

        if not candidates:
            return None

        scored_recipes = []
        for recipe in candidates:
            score = self._calculate_macro_score(recipe, target_macros)
            scored_recipes.append((recipe, score))

        scored_recipes.sort(key=lambda x: x[1], reverse=True)

        top_n = scored_recipes[:5]
        best_match = random.choice(top_n)[0]

        return best_match

    def _calculate_target_macros(self, profile, meal_type):
        dist = self.MEAL_DISTRIBUTIONS.get(meal_type, 0.30)
        """Calculate target macros for the given meal type based on profile"""
        return {
            'calories': float(profile.daily_calories or 2000) * dist,
            'protein': float(profile.daily_protein or 150) * dist,
            'carbs': float(profile.daily_carbohydrates or 250) * dist,
            'fat': float(profile.daily_fat or 70) * dist,
        }

    def _calculate_macro_score(self, recipe, targets):
        """Calculate a score (0-100) for how well the recipe matches the target macros"""
        weights = {'protein': 2.0, 'carbs': 1.0, 'fat': 1.0}
        scores = []

        for macro in ['protein', 'carbs', 'fat']:
            target_val = targets[macro]
            model_field = 'carbohydrate' if macro == 'carbs' else macro

            recipe_val = float(getattr(recipe, model_field) or 0)

            if target_val == 0:
                target_val = 1

            diff = abs(recipe_val - target_val)
            percent_off = diff / target_val

            score = max(0, 100 - (percent_off * 100))
            scores.append(score * weights[macro])

        final_score = sum(scores) / sum(weights.values())
        return final_score