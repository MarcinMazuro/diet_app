from rest_framework import serializers
from .models import Meal, Rating
from recipes.serializers import SingleRecipeSerializer


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for meal plans"""
    recipe = SingleRecipeSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Meal
        fields = ['id', 'recipe', 'recipe_id', 'date', 'meal_type', 'source']
        read_only_fields = ['id', 'source']


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for recipe ratings"""
    recipe = SingleRecipeSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'recipe_id', 'rating', 'interacted_at']
        read_only_fields = ['id', 'interacted_at']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


