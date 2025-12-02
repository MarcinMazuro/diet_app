from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from profiles.models import Profile
from recipes.serializers import  SingleRecipeSerializer
from .models import Recommendation, Rating
from .services import RecipeMatcher, MealPlanner


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_recipe(request):
    """
    Get recipe recommendations for a specific meal type

    Query params:
    - meal_type: BREAKFAST, LUNCH, or DINNER (default: BREAKFAST)
    """
    meal_type = request.GET.get('meal_type', 'BREAKFAST')


    matcher = RecipeMatcher()
    recipe = matcher.find_best_recipe(
        profile=Profile.objects.get(user=request.user),
        meal_type=meal_type,
    )

    if not recipe:
        return Response(
            {"detail": "No matching recipes found. Try adjusting your filters or nutritional goals."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Save recommendations to database
    rec_obj = Recommendation.objects.create(
        profile=Profile.objects.get(user=request.user),
        recipe=recipe,
    )

    serializer = SingleRecipeSerializer(recipe)
    data = serializer.data
    data['recommendation_id'] = rec_obj.id

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_daily_plan(request):
    """
    Generate a complete daily meal plan (breakfast, lunch, dinner, snack)

    """

    planner = MealPlanner()
    plan = planner.create_meal_plan(
        profile=Profile.objects.get(user=request.user),
    )

    if not plan:
        return Response(
            {"detail": "Could not generate meal plan. Please check your profile settings."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Save to database
    planner.save_meal_plan(plan, Profile.objects.get(user=request.user))

    # Return plan with deviation info
    response_data = plan.to_dict()
    response_data['deviations'] = plan.get_deviation_from_target(Profile.objects.get(user=request.user))

    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations_history(request):
    """
    Get the recommendation history for the authenticated user
    """
    profile = Profile.objects.get(user=request.user)
    recommendations = Recommendation.objects.filter(profile=profile).order_by('-recommended_at')

    history = []
    for rec in recommendations:
        history.append({
            'recommendation_id': rec.id,
            'recipe_id': rec.recipe.id,
            'recipe_name': rec.recipe.name,
            'recommended_at': rec.recommended_at,
        })

    return Response({'history': history})


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def rate_recipe(request, recipe_id=None):
    """
    Create or update a rating for a recipe (1-5 stars)

    Body params:
    - recipe_id: ID of the recipe (required if not in URL)
    - rating: Rating value 1-5 (required)
    """
    # Get recipe_id from URL or body
    if not recipe_id:
        recipe_id = request.data.get('recipe_id')

    rating_value = request.data.get('rating')

    if not recipe_id:
        return Response(
            {"detail": "recipe_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not rating_value:
        return Response(
            {"detail": "rating is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            return Response(
                {"detail": "Rating must be between 1 and 5."},
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValueError:
        return Response(
            {"detail": "Rating must be a number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if recipe exists
    from recipes.models import Recipe
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return Response(
            {"detail": "Recipe not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Create or update rating
    profile = Profile.objects.get(user=request.user)
    rating_obj, created = Rating.objects.update_or_create(
        profile=profile,
        recipe=recipe,
        defaults={'rating': rating_value}
    )

    return Response({
        "detail": "Rating saved successfully.",
        "rating_id": rating_obj.id,
        "recipe_id": recipe.id,
        "recipe_name": recipe.name,
        "rating": rating_value,
        "created": created
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rating(request, recipe_id):
    """
    Get user's rating for a specific recipe

    URL params:
    - recipe_id: ID of the recipe
    """
    profile = Profile.objects.get(user=request.user)

    try:
        rating = Rating.objects.get(profile=profile, recipe_id=recipe_id)
    except Rating.DoesNotExist:
        return Response(
            {"detail": "Rating not found for this recipe."},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        "rating_id": rating.id,
        "recipe_id": rating.recipe.id,
        "recipe_name": rating.recipe.name,
        "rating": rating.rating,
        "interacted_at": rating.interacted_at
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_rating(request, recipe_id):
    """
    Delete user's rating for a specific recipe

    URL params:
    - recipe_id: ID of the recipe
    """
    profile = Profile.objects.get(user=request.user)

    try:
        rating = Rating.objects.get(profile=profile, recipe_id=recipe_id)
        rating.delete()
        return Response(
            {"detail": "Rating deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    except Rating.DoesNotExist:
        return Response(
            {"detail": "Rating not found for this recipe."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ratings_history(request):
    """
    Get the ratings history for the authenticated user
    """
    profile = Profile.objects.get(user=request.user)
    ratings = Rating.objects.filter(profile=profile).order_by('-interacted_at')

    history = []
    for rating in ratings:
        history.append({
            'recipe_id': rating.recipe.id,
            'recipe_name': rating.recipe.name,
            'rating': rating.rating,
            'interacted_at': rating.interacted_at,
        })

    return Response({'history': history})


