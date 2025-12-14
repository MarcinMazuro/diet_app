from rest_framework import status
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from profiles.models import Profile
from recipes.models import Recipe
from .models import MealType


def get_user_profile(request):
    """Get the profile for the authenticated user"""
    return Profile.objects.get(user=request.user)


def validate_date(date_string):
    """
    Validate and parse date string
    Returns tuple: (parsed_date, error_response)
    """
    if not date_string:
        return None, Response(
            {"detail": "date is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    dt = parse_date(date_string)
    if not dt:
        return None, Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD (e.g., 2025-12-07)."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return dt, None


def validate_meal_type(meal_type):
    """
    Validate meal type
    Returns error_response or None if valid
    """
    if not meal_type:
        return Response(
            {"detail": "meal_type is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    meal_type = meal_type.lower()

    if meal_type not in [MealType.BREAKFAST, MealType.DINNER, MealType.LUNCH, MealType.SNACK]:
        return Response(
            {"detail": "Invalid meal_type. Must be breakfast, lunch, dinner, or snack."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return None


def get_recipe_or_404(recipe_id):
    """
    Get recipe by ID or return 404 response
    Returns tuple: (recipe, error_response)
    """
    if not recipe_id:
        return None, Response(
            {"detail": "recipe_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        recipe = Recipe.objects.get(id=recipe_id)
        return recipe, None
    except Recipe.DoesNotExist:
        return None, Response(
            {"detail": "Recipe not found."},
            status=status.HTTP_404_NOT_FOUND
        )

