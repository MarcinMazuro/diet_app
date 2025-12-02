from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Recipe
from .serializers import ListRecipeSerializer, SingleRecipeSerializer


@api_view(['GET'])
def list_recipes(request):
    """Returns a list of recipes with optional filters via query params:
       ?name=... & ?category=... & ?min_calories=... & ?max_calories=...
       Pagination supported via ?page=... & ?page_size=...
       Sorting supported via ?ordering=... (e.g., name, calories, -calories for descending)
    """
    qs = Recipe.objects.all()

    name = request.GET.get('name')
    category = request.GET.get('category')
    min_cal = request.GET.get('min_calories')
    max_cal = request.GET.get('max_calories')
    ordering = request.GET.get('ordering')

    if name:
        qs = qs.filter(name__icontains=name)

    if category:
        qs = qs.filter(categories__name__iexact=category)

    if min_cal:
        try:
            qs = qs.filter(calories__gte=float(min_cal))
        except (ValueError, TypeError):
            pass

    if max_cal:
        try:
            qs = qs.filter(calories__lte=float(max_cal))
        except (ValueError, TypeError):
            pass

    qs = qs.distinct()

    # Apply ordering
    if ordering:
        allowed_ordering = [
            'name', '-name',
            'calories', '-calories',
            'protein', '-protein',
            'fat', '-fat',
            'carbohydrate', '-carbohydrate',
            'preparation_time', '-preparation_time',
            'created_at', '-created_at'
        ]
        if ordering in allowed_ordering:
            qs = qs.order_by(ordering)
        else:
            # Default ordering if invalid value provided
            qs = qs.order_by('name')
    else:
        qs = qs.order_by('name')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginator.page_size_query_param = 'page_size'
    paginator.max_page_size = 100

    page = paginator.paginate_queryset(qs, request)
    if page is not None:
        serializer = ListRecipeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = ListRecipeSerializer(qs, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_recipe(request, recipe_id):
    """Returns a specific recipe by ID"""
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SingleRecipeSerializer(recipe)
    return Response(serializer.data)
