from rest_framework import serializers

from .models import Recipe, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']


class SingleRecipeSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

class ListRecipeSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'preparation_time',
            'calories', 'image_url', 'categories', 'servings'
        ]

