from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Recipe, Category, RecipeCategory


class RecipeModelTest(TestCase):
    """Test models for Recipe and Category"""

    def setUp(self):
        self.category = Category.objects.create(name="Breakfast", type="meal_type")
        self.recipe = Recipe.objects.create(
            name="Scrambled Eggs",
            description="Quick and easy breakfast",
            calories=200.0,
            protein=15.0,
            fat=10.0,
            carbohydrate=5.0,
            servings=2,
            preparation_time=10
        )
        RecipeCategory.objects.create(recipe=self.recipe, category=self.category)

    def test_recipe_creation(self):
        """Test that recipe is created correctly"""
        self.assertEqual(self.recipe.name, "Scrambled Eggs")
        self.assertEqual(self.recipe.calories, 200.0)
        self.assertEqual(self.recipe.categories.count(), 1)

    def test_category_creation(self):
        """Test that category is created correctly"""
        self.assertEqual(self.category.name, "Breakfast")
        self.assertEqual(self.category.type, "meal_type")

    def test_recipe_str(self):
        """Test string representation of recipe"""
        self.assertEqual(str(self.recipe), "Scrambled Eggs")

    def test_category_str(self):
        """Test string representation of category"""
        self.assertEqual(str(self.category), "Breakfast")


class RecipeAPITest(APITestCase):
    """Test Recipe API endpoints"""

    def setUp(self):
        """Create test data"""
        # Create categories
        self.breakfast = Category.objects.create(name="Breakfast", type="meal_type")
        self.lunch = Category.objects.create(name="Lunch", type="meal_type")
        self.healthy = Category.objects.create(name="Healthy", type="diet")

        # Create recipes
        self.recipe1 = Recipe.objects.create(
            name="Scrambled Eggs",
            description="Quick breakfast",
            calories=200.0,
            protein=15.0,
            fat=10.0,
            carbohydrate=5.0,
            servings=2,
            preparation_time=10,
            ingredients=["2 eggs", "butter", "salt"],
            directions=["Beat eggs", "Cook in pan"]
        )
        RecipeCategory.objects.create(recipe=self.recipe1, category=self.breakfast)

        self.recipe2 = Recipe.objects.create(
            name="Grilled Chicken",
            description="Healthy lunch option",
            calories=350.0,
            protein=40.0,
            fat=15.0,
            carbohydrate=10.0,
            servings=1,
            preparation_time=30,
            ingredients=["chicken breast", "olive oil", "spices"],
            directions=["Season chicken", "Grill for 15 minutes"]
        )
        RecipeCategory.objects.create(recipe=self.recipe2, category=self.lunch)
        RecipeCategory.objects.create(recipe=self.recipe2, category=self.healthy)

        self.recipe3 = Recipe.objects.create(
            name="Caesar Salad",
            description="Classic salad",
            calories=180.0,
            protein=8.0,
            fat=12.0,
            carbohydrate=15.0,
            servings=2,
            preparation_time=15
        )
        RecipeCategory.objects.create(recipe=self.recipe3, category=self.lunch)

        # Create more recipes for pagination testing
        for i in range(15):
            recipe = Recipe.objects.create(
                name=f"Test Recipe {i}",
                description=f"Test description {i}",
                calories=100.0 + i * 10,
                protein=10.0,
                fat=5.0,
                carbohydrate=15.0
            )
            RecipeCategory.objects.create(recipe=recipe, category=self.breakfast)

    def test_list_recipes(self):
        """Test listing all recipes (with pagination)"""
        url = reverse('list-recipes')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 18)  # Total recipes
        self.assertEqual(len(response.data['results']), 10)  # Default page size

    def test_get_recipe_detail(self):
        """Test getting a specific recipe by ID"""
        url = reverse('get-recipe', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Scrambled Eggs")
        self.assertEqual(response.data['calories'], 200.0)
        self.assertIn('ingredients', response.data)
        self.assertEqual(len(response.data['ingredients']), 3)

    def test_get_recipe_not_found(self):
        """Test getting a non-existent recipe"""
        url = reverse('get-recipe', kwargs={'recipe_id': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_filter_by_name(self):
        """Test filtering recipes by name"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'name': 'chicken'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "Grilled Chicken")

    def test_filter_by_name_partial(self):
        """Test filtering recipes by partial name match"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'name': 'egg'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_filter_by_category(self):
        """Test filtering recipes by category"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'category': 'Lunch'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        # Check that both lunch recipes are returned
        names = [r['name'] for r in response.data['results']]
        self.assertIn("Grilled Chicken", names)
        self.assertIn("Caesar Salad", names)

    def test_filter_by_min_calories(self):
        """Test filtering recipes by minimum calories"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'min_calories': '300'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return recipes with >= 300 calories
        for recipe in response.data['results']:
            self.assertGreaterEqual(recipe['calories'], 300.0)

    def test_filter_by_max_calories(self):
        """Test filtering recipes by maximum calories"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'max_calories': '200'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return recipes with <= 200 calories
        for recipe in response.data['results']:
            self.assertLessEqual(recipe['calories'], 200.0)

    def test_filter_by_calorie_range(self):
        """Test filtering recipes by calorie range"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'min_calories': '150', 'max_calories': '250'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return recipes with 150 <= calories <= 250
        for recipe in response.data['results']:
            self.assertGreaterEqual(recipe['calories'], 150.0)
            self.assertLessEqual(recipe['calories'], 250.0)

    def test_combined_filters(self):
        """Test combining multiple filters"""
        url = reverse('list-recipes')
        response = self.client.get(url, {
            'category': 'Lunch',
            'min_calories': '300'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "Grilled Chicken")

    def test_pagination_default(self):
        """Test default pagination (10 items per page)"""
        url = reverse('list-recipes')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_pagination_second_page(self):
        """Test getting second page"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'page': '2'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 8)  # Remaining recipes
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_pagination_custom_page_size(self):
        """Test custom page size"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'page_size': '5'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next'])

    def test_pagination_max_page_size(self):
        """Test that page size is limited to max (100)"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'page_size': '200'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all 18 recipes (less than max of 100)
        self.assertEqual(len(response.data['results']), 18)

    def test_invalid_calorie_filter(self):
        """Test that invalid calorie values are handled gracefully"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'min_calories': 'invalid'})

        # Should still return 200, just ignore the invalid filter
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 18)

    def test_empty_results(self):
        """Test filtering that returns no results"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'name': 'nonexistent recipe xyz'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_ordering_by_name_ascending(self):
        """Test ordering recipes by name (ascending)"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'ordering': 'name', 'page_size': '5'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r['name'] for r in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_ordering_by_name_descending(self):
        """Test ordering recipes by name (descending)"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'ordering': '-name', 'page_size': '5'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r['name'] for r in response.data['results']]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_ordering_by_calories_ascending(self):
        """Test ordering recipes by calories (ascending)"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'ordering': 'calories', 'page_size': '5'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        calories = [r['calories'] for r in response.data['results']]
        self.assertEqual(calories, sorted(calories))

    def test_ordering_by_calories_descending(self):
        """Test ordering recipes by calories (descending)"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'ordering': '-calories', 'page_size': '5'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        calories = [r['calories'] for r in response.data['results']]
        self.assertEqual(calories, sorted(calories, reverse=True))



    def test_ordering_invalid_field(self):
        """Test that invalid ordering field defaults to name ordering"""
        url = reverse('list-recipes')
        response = self.client.get(url, {'ordering': 'invalid_field', 'page_size': '5'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should default to ordering by name
        names = [r['name'] for r in response.data['results']]
        self.assertEqual(names, sorted(names))

    def test_ordering_with_filters(self):
        """Test combining ordering with filters"""
        url = reverse('list-recipes')
        response = self.client.get(url, {
            'category': 'Breakfast',
            'ordering': '-calories',
            'page_size': '5'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All results should be from Breakfast category and ordered by calories desc
        calories = [r['calories'] for r in response.data['results']]
        self.assertEqual(calories, sorted(calories, reverse=True))
