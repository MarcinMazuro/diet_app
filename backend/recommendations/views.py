from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from recipes.serializers import SingleRecipeSerializer
from .models import Plan, Rating, PlanSource, MealType
from .services import RecipeMatcher, MealPlanner
from .utils import get_user_profile, validate_date, validate_meal_type, get_recipe_or_404


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def select_recipe(request):
    """
    Select a recommended recipe to include in the user's meal plan

    Body params:
    - recipe_id: ID of the recipe to add to plan (required)
    - date: Date in YYYY-MM-DD format (required)
    - meal_type: BREAKFAST, LUNCH, DINNER, or SNACK (required)
    """
    profile = get_user_profile(request)

    recipe_id = request.data.get('recipe_id')
    date = request.data.get('date')
    meal_type = request.data.get('meal_type')

    recipe, error = get_recipe_or_404(recipe_id)
    if error:
        return error

    dt, error = validate_date(date)
    if error:
        return error

    error = validate_meal_type(meal_type)
    if error:
        return error

    plan, created = Plan.objects.update_or_create(
        profile=profile,
        date=dt,
        meal_type=meal_type,
        defaults={
            'recipe': recipe,
            'source': PlanSource.USER_SELECTED
        }
    )
    return Response({
        "detail": "Plan saved successfully.",
        "recipe_name": recipe.name,
        "meal_type": meal_type,
        "date": plan.date,
        "created": created
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_plan(request, plan_id):
    """
    Delete a meal plan entry

    URL params:
    - plan_id: ID of the plan to delete
    """
    profile = get_user_profile(request)
    try:
        plan = Plan.objects.get(id=plan_id, profile=profile)
        plan.delete()
        return Response(
            {"detail": "Plan deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    except Plan.DoesNotExist:
        return Response(
            {"detail": "Plan not found."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_plans(request):
    """
    Get the meal plans for the authenticated user

    Query params:
    - date: Date in YYYY-MM-DD format (required)
    - meal_type: BREAKFAST, LUNCH, DINNER, or SNACK (optional - returns all if not specified)
    """
    profile = get_user_profile(request)

    date = request.query_params.get('date')
    meal_type = request.query_params.get('meal_type')

    dt, error = validate_date(date)
    if error:
        return error

    plans = Plan.objects.filter(profile=profile, date=dt)

    if meal_type:
        error = validate_meal_type(meal_type)
        if error:
            return error
        plans = plans.filter(meal_type=meal_type)

    plan_list = []
    for plan in plans:
        plan_list.append({
            'plan_id': plan.id,
            'recipe_id': plan.recipe.id,
            'recipe_name': plan.recipe.name,
            'date': plan.date,
            'meal_type': plan.meal_type,
            'source': plan.source,
        })

    return Response({'plans': plan_list})


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def recommend_recipe(request):
    """
    Get recipe recommendations for a specific meal type

    Query params:
    - date: Date in YYYY-MM-DD format (required)
    - meal_type: BREAKFAST, LUNCH, DINNER, or SNACK (required)
    """
    profile = get_user_profile(request)

    date = request.data.get('date')
    meal_type = request.data.get('meal_type')

    dt, error = validate_date(date)
    if error:
        return error

    error = validate_meal_type(meal_type)
    if error:
        return error

    matcher = RecipeMatcher()
    recipe = matcher.find_best_recipe(
        profile=profile,
        meal_type=meal_type,
    )

    if not recipe:
        return Response(
            {"detail": "No matching recipes found. Try adjusting your filters or nutritional goals."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Save recommendations to database
    plan, created = Plan.objects.update_or_create(
        profile=profile,
        date=dt,
        meal_type=meal_type,
        defaults={
            'recipe': recipe,
            'source': PlanSource.AI_GENERATED
        }
    )

    serializer = SingleRecipeSerializer(recipe)
    data = serializer.data
    data['recommendation_id'] = plan.id

    return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)



@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def generate_daily_plan(request):
    """
    Generate a complete daily meal plan (breakfast, lunch, dinner, snack)

    Body params:
    - date: Date in YYYY-MM-DD format (required)
    """
    profile = get_user_profile(request)
    date = request.data.get('date')

    dt, error = validate_date(date)
    if error:
        return error

    planner = MealPlanner()
    meal_plan = planner.create_meal_plan(profile=profile)

    if not meal_plan:
        return Response(
            {"detail": "Could not generate meal plan. Please check your profile settings."},
            status=status.HTTP_404_NOT_FOUND
        )

    if meal_plan.breakfast:
        Plan.objects.update_or_create(
            profile=profile,
            date=dt,
            meal_type=MealType.BREAKFAST,
            defaults={
                'recipe': meal_plan.breakfast,
                'source': PlanSource.AI_GENERATED
            }
        )

    if meal_plan.lunch:
        Plan.objects.update_or_create(
            profile=profile,
            date=dt,
            meal_type=MealType.LUNCH,
            defaults={
                'recipe': meal_plan.lunch,
                'source': PlanSource.AI_GENERATED
            }
        )

    if meal_plan.dinner:
        Plan.objects.update_or_create(
            profile=profile,
            date=dt,
            meal_type=MealType.DINNER,
            defaults={
                'recipe': meal_plan.dinner,
                'source': PlanSource.AI_GENERATED
            }
        )

    if meal_plan.snack:
        Plan.objects.update_or_create(
            profile=profile,
            date=dt,
            meal_type=MealType.SNACK,
            defaults={
                'recipe': meal_plan.snack,
                'source': PlanSource.AI_GENERATED
            }
        )

    # Return plan with deviation info
    response_data = meal_plan.to_dict()
    response_data['deviations'] = meal_plan.get_deviation_from_target(profile)
    response_data['date'] = dt

    return Response(response_data)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def rate_recipe(request, recipe_id=None):
    """
    Create or update a rating for a recipe (1-5 stars)

    Body params:
    - recipe_id: ID of the recipe (required if not in URL)
    - rating: Rating value 1-5 (required)
    """
    profile = get_user_profile(request)

    # Get recipe_id from URL or body
    if not recipe_id:
        recipe_id = request.data.get('recipe_id')

    rating_value = request.data.get('rating')

    # Validate recipe
    recipe, error = get_recipe_or_404(recipe_id)
    if error:
        return error

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

    # Create or update rating
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
    profile = get_user_profile(request)

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
    profile = get_user_profile(request)

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
    profile = get_user_profile(request)
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


