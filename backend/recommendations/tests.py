from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CustomUser
from recipes.models import Recipe, Category, RecipeCategory
from .models import Rating


class RatingCRUDTest(APITestCase):
    """Test CRUD operations for Recipe Ratings"""

    def setUp(self):
        """Create test user, profile, and recipes"""
        # Create user (profile is auto-created by signal)
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
        self.profile.gender = 'M'
        self.profile.height = 180
        self.profile.weight = 75
        self.profile.physical_activity = 'MODERATE'
        self.profile.nutritional_goal = 'MAINTAIN'
        self.profile.save()

        # Create another user for testing isolation
        self.user2 = CustomUser.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.profile2 = self.user2.profile
        self.profile2.gender = 'F'
        self.profile2.height = 165
        self.profile2.weight = 60
        self.profile2.physical_activity = 'MODERATE'
        self.profile2.nutritional_goal = 'MAINTAIN'
        self.profile2.save()

        # Create categories
        self.breakfast = Category.objects.create(name="Breakfast", type="meal_type")
        self.lunch = Category.objects.create(name="Lunch", type="meal_type")

        # Create recipes
        self.recipe1 = Recipe.objects.create(
            name="Scrambled Eggs",
            description="Quick breakfast",
            calories=200.0,
            protein=15.0,
            fat=10.0,
            carbohydrate=5.0,
            servings=2,
            preparation_time=10
        )
        RecipeCategory.objects.create(recipe=self.recipe1, category=self.breakfast)

        self.recipe2 = Recipe.objects.create(
            name="Grilled Chicken",
            description="Healthy lunch",
            calories=350.0,
            protein=40.0,
            fat=15.0,
            carbohydrate=10.0,
            servings=1,
            preparation_time=30
        )
        RecipeCategory.objects.create(recipe=self.recipe2, category=self.lunch)

        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_create_rating(self):
        """Test creating a new rating"""
        url = reverse('ratings_list')
        data = {
            'recipe_id': self.recipe1.id,
            'rating': 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['recipe_id'], self.recipe1.id)
        self.assertTrue(response.data['created'])

        # Verify rating was saved in database
        rating = Rating.objects.get(profile=self.profile, recipe=self.recipe1)
        self.assertEqual(rating.rating, 5)

    def test_create_rating_missing_recipe_id(self):
        """Test creating rating without recipe_id"""
        url = reverse('ratings_list')
        data = {'rating': 5}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('recipe_id', response.data['detail'])

    def test_create_rating_missing_rating_value(self):
        """Test creating rating without rating value"""
        url = reverse('ratings_list')
        data = {'recipe_id': self.recipe1.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data['detail'])

    def test_create_rating_invalid_range(self):
        """Test creating rating with invalid range"""
        url = reverse('ratings_list')

        # Test rating too low
        data = {'recipe_id': self.recipe1.id, 'rating': 0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test rating too high
        data = {'recipe_id': self.recipe1.id, 'rating': 6}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rating_invalid_type(self):
        """Test creating rating with non-numeric value"""
        url = reverse('ratings_list')
        data = {'recipe_id': self.recipe1.id, 'rating': 'five'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('number', response.data['detail'])

    def test_create_rating_nonexistent_recipe(self):
        """Test creating rating for non-existent recipe"""
        url = reverse('ratings_list')
        data = {'recipe_id': 99999, 'rating': 5}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Recipe not found', response.data['detail'])

    def test_update_rating(self):
        """Test updating an existing rating"""
        # Create initial rating
        Rating.objects.create(profile=self.profile, recipe=self.recipe1, rating=3)

        # Update rating
        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        data = {'rating': 5}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertFalse(response.data['created'])

        # Verify rating was updated in database
        rating = Rating.objects.get(profile=self.profile, recipe=self.recipe1)
        self.assertEqual(rating.rating, 5)

    def test_get_rating(self):
        """Test getting a specific rating"""
        # Create rating
        Rating.objects.create(profile=self.profile, recipe=self.recipe1, rating=4)

        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['recipe_id'], self.recipe1.id)
        self.assertEqual(response.data['recipe_name'], 'Scrambled Eggs')
        self.assertIn('interacted_at', response.data)

    def test_get_rating_not_found(self):
        """Test getting rating that doesn't exist"""
        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Rating not found', response.data['detail'])

    def test_delete_rating(self):
        """Test deleting a rating"""
        # Create rating
        Rating.objects.create(profile=self.profile, recipe=self.recipe1, rating=4)

        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify rating was deleted from database
        self.assertFalse(Rating.objects.filter(profile=self.profile, recipe=self.recipe1).exists())

    def test_delete_rating_not_found(self):
        """Test deleting rating that doesn't exist"""
        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Rating not found', response.data['detail'])

    def test_get_all_ratings(self):
        """Test getting all ratings for authenticated user"""
        # Create multiple ratings
        Rating.objects.create(profile=self.profile, recipe=self.recipe1, rating=5)
        Rating.objects.create(profile=self.profile, recipe=self.recipe2, rating=4)

        url = reverse('ratings_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ratings', response.data)
        self.assertEqual(len(response.data['ratings']), 2)

        # Verify ratings are ordered by interacted_at (descending)
        ratings = response.data['ratings']
        self.assertEqual(ratings[0]['rating'], 4)  # recipe2 (more recent)
        self.assertEqual(ratings[1]['rating'], 5)  # recipe1

    def test_user_isolation(self):
        """Test that users can only access their own ratings"""
        # Create rating for user1
        Rating.objects.create(profile=self.profile, recipe=self.recipe1, rating=5)

        # Create rating for user2
        Rating.objects.create(profile=self.profile2, recipe=self.recipe1, rating=3)

        # User1 should only see their own rating
        url = reverse('ratings_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['ratings']), 1)
        self.assertEqual(response.data['ratings'][0]['rating'], 5)

        # Switch to user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['ratings']), 1)
        self.assertEqual(response.data['ratings'][0]['rating'], 3)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access rating endpoints"""
        self.client.force_authenticate(user=None)

        # Test create
        url = reverse('ratings_list')
        response = self.client.post(url, {'recipe_id': self.recipe1.id, 'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test get
        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test delete
        url = reverse('rating_detail', kwargs={'recipe_id': self.recipe1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test list
        url = reverse('ratings_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unique_constraint(self):
        """Test that a user can only have one rating per recipe"""
        # Create first rating
        url = reverse('ratings_list')
        data = {'recipe_id': self.recipe1.id, 'rating': 3}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to create second rating for same recipe - should update instead
        data = {'recipe_id': self.recipe1.id, 'rating': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['created'])

        # Verify only one rating exists
        count = Rating.objects.filter(profile=self.profile, recipe=self.recipe1).count()
        self.assertEqual(count, 1)

        # Verify rating was updated
        rating = Rating.objects.get(profile=self.profile, recipe=self.recipe1)
        self.assertEqual(rating.rating, 5)


