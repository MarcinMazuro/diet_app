from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from profiles.models import Profile
from recipes.serializers import RecipeSerializer
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

    serializer = RecipeSerializer(recipe)
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



@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Not tested yet
def rate_recipe(request):
    """
    Rate a recipe (1-5 stars)

    Body params:
    - recipe_id: ID of the recipe (required)
    """
    recipe_id = request.data.get('recipe_id')
    rating = request.data.get('rating')

    if not recipe_id or not rating:
        return Response(
            {"detail": "recipe_id and rating are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return Response(
                {"detail": "Rating must be between 1 and 5."},
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValueError:
        return Response(
            {"detail": "Rating must be a number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create or update interaction
    interaction, created = Rating.objects.update_or_create(
        profile=Profile.objects.get(user=request.user),
        recipe_id=recipe_id,
        defaults={'rating': rating}
    )

    return Response({
        "detail": "Rating saved successfully.",
        "rating": rating
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


