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
    """Returns a list of all recipes"""
    recipes = Recipe.objects.all()
    serializer = RecipeSerializer(recipes, many=True)
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
