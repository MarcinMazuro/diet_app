from rest_framework import serializers
from .models import Recommendation, Rating
from recipes.serializers import SingleRecipeSerializer


class RecipeRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for recipe recommendations"""
    recipe = SingleRecipeSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'recipe', 'recommended_at']
        read_only_fields = ['id', 'recommended_at']


class RecipeInteractionSerializer(serializers.ModelSerializer):
    """Serializer for recipe interactions (ratings)"""
    recipe = SingleRecipeSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'recipe_id', 'rating']
        read_only_fields = ['id', 'recipe']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class MealPlanSerializer(serializers.Serializer):
    """Serializer for meal plan response"""
    breakfast = SingleRecipeSerializer(read_only=True, allow_null=True)
    lunch = SingleRecipeSerializer(read_only=True, allow_null=True)
    dinner = SingleRecipeSerializer(read_only=True, allow_null=True)

    totals = serializers.DictField(read_only=True)
    deviations = serializers.DictField(read_only=True, required=False)
    day = serializers.IntegerField(read_only=True, required=False)


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recommendation request parameters"""
    meal_type = serializers.ChoiceField(
        choices=['BREAKFAST', 'LUNCH', 'DINNER'],
        default='BREAKFAST'
    )
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)
    max_prep_time = serializers.IntegerField(min_value=1, required=False)
    category = serializers.CharField(max_length=100, required=False)


class DailyPlanRequestSerializer(serializers.Serializer):
    """Serializer for daily plan request parameters"""
    max_prep_time = serializers.IntegerField(min_value=1, required=False)
    category = serializers.CharField(max_length=100, required=False)
    max_attempts = serializers.IntegerField(min_value=1, max_value=20, default=10)


class RatingRequestSerializer(serializers.Serializer):
    """Serializer for rating request"""
    recipe_id = serializers.IntegerField(required=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)

