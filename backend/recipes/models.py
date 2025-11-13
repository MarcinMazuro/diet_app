from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50)  # np. 'cuisine', 'diet', 'meal_type'

    class Meta:
        verbose_name_plural = "categories"
        db_table = "Categories"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    source = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    ingredients = models.JSONField(default=list)  # lista składników
    directions = models.JSONField(default=list)  # lista kroków
    servings = models.IntegerField(null=True, blank=True)
    preparation_time = models.IntegerField(null=True, blank=True)  # w minutach

    # Wartości odżywcze
    fiber = models.FloatField(null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    saturated_fat = models.FloatField(null=True, blank=True)
    carbohydrate = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    sodium = models.FloatField(null=True, blank=True)

    image_url = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, through='RecipeCategory')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Recipes"

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'category')
        db_table = "Recipes_Categories"
