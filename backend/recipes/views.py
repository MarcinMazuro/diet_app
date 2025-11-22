from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe
from .serializers import RecipeSerializer


@api_view(['GET'])
def random_recipe(request):
    """Returns a random recipe"""
    recipe = Recipe.objects.order_by('?').first()
    if not recipe:
        return Response({'error': 'No recipes available'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RecipeSerializer(recipe)
    return Response(serializer.data)



@api_view(['GET'])
def list_recipes(request):
    """Returns a list of recipes with optional filters via query params:
       ?name=... & ?category=... & ?min_calories=... & ?max_calories=...
    """
    qs = Recipe.objects.all()

    name = request.GET.get('name')
    category = request.GET.get('category')
    min_cal = request.GET.get('min_calories')
    max_cal = request.GET.get('max_calories')

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
    serializer = RecipeSerializer(qs, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_recipe(request, recipe_id):
    """Returns a specific recipe by ID"""
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RecipeSerializer(recipe)
    return Response(serializer.data)
