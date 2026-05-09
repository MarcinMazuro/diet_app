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
    ingredients = models.JSONField(default=list)
    directions = models.JSONField(default=list)
    servings = models.IntegerField(null=True, blank=True)
    preparation_time = models.IntegerField(null=True, blank=True)

    fiber = models.FloatField(null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    saturated_fat = models.FloatField(null=True, blank=True)
    carbohydrate = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    sodium = models.FloatField(null=True, blank=True)

    image_url = models.URLField(blank=True, null=True)
    aggregated_nutrients = models.JSONField(default=list)
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


class Ingredient(models.Model):
    canonical_name = models.CharField(max_length=255, unique=True)
    fdc_id = models.IntegerField(null=True, blank=True, db_index=True)
    fdc_description = models.CharField(max_length=500, null=True, blank=True)
    fdc_category = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "Ingredients"

    def __str__(self):
        return self.canonical_name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='structured_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_uses')
    raw_text = models.CharField(max_length=500)
    quantity_in_grams = models.FloatField(null=True, blank=True)
    preparation = models.CharField(max_length=200, null=True, blank=True)
    parse_confidence = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "Recipe_Ingredients"


class Nutrient(models.Model):
    fdc_nutrient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    class Meta:
        db_table = "Nutrients"

    def __str__(self):
        return f"{self.name} ({self.unit})"


class IngredientNutrient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='nutrient_values')
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    value_per_100g = models.FloatField()

    class Meta:
        db_table = "Ingredient_Nutrients"
        unique_together = ('ingredient', 'nutrient')
