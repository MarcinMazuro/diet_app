from django.db import models

from profiles.models import Profile
from recipes.models import Recipe

class MealSource(models.TextChoices):
    AI_GENERATED = 'ai_generated',
    USER_SELECTED = 'user_selected',

class MealType(models.TextChoices):
    BREAKFAST = 'breakfast',
    LUNCH = 'lunch',
    DINNER = 'dinner',
    SNACK = 'snack',


class Meal(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='meals')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date = models.DateField()
    source = models.CharField(max_length=20, choices=MealSource.choices, default=MealSource.AI_GENERATED)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)

    class Meta:
        db_table = "Meals"
        unique_together = ('profile', 'date', 'meal_type')

    def __str__(self):
        return f"{self.profile.user.username} - {self.date} - {self.meal_type}"

# For user rating
class Rating(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    rating = models.IntegerField(null=True, blank=True)  # 1-5 gwiazdek
    interacted_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Ratings"
        unique_together = ('profile', 'recipe')

    def __str__(self):
        return f"{self.profile.user.username} - {self.recipe.name} - {self.rating}★"
