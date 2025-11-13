from rest_framework import serializers
from .models import Profile
from datetime import date

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the profile owner."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)

    # Display fields for choices (read-only)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    nutritional_goal_display = serializers.CharField(source='get_nutritional_goal_display', read_only=True)
    physical_activity_display = serializers.CharField(source='get_physical_activity_display', read_only=True)
    calculation_method_display = serializers.CharField(source='get_calculation_method_display', read_only=True)
    
    # Calculated fields
    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'gender', 'gender_display',
            'nutritional_goal', 'nutritional_goal_display',
            'physical_activity', 'physical_activity_display',
            'calculation_method', 'calculation_method_display',
            'calorie_adjustment',
            'weight', 'height', 'date_of_birth', 'age',
            'bmi', 'ppm', 'cpm', 'daily_calories',
            'daily_protein', 'daily_carbohydrates', 'daily_fat',
            'calculations_last_updated',
            'updated_at', 'date_joined'
        ]
        read_only_fields = [
            'username', 'email', 'date_joined', 'age',
            'gender_display', 'nutritional_goal_display', 
            'physical_activity_display', 'calculation_method_display',
            'bmi', 'ppm', 'cpm', 'daily_calories',
            'daily_protein', 'daily_carbohydrates', 'daily_fat',
            'calculations_last_updated', 'updated_at'
        ]

    def get_age(self, obj):
        """Return calculated age"""
        return obj.calculate_age()

    def validate_date_of_birth(self, value):
        """Validate that date of birth is reasonable"""
        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 13:
                raise serializers.ValidationError("User must be at least 13 years old.")
            if age > 120:
                raise serializers.ValidationError("Invalid date of birth.")
            if value > today:
                raise serializers.ValidationError("Date of birth cannot be in the future.")
        
        return value

    def validate_weight(self, value):
        """Validate weight is within reasonable range"""
        if value is not None:
            if value < 20:
                raise serializers.ValidationError("Weight must be at least 20 kg.")
            if value > 500:
                raise serializers.ValidationError("Weight must be at most 500 kg.")
        return value

    def validate_height(self, value):
        """Validate height is within reasonable range"""
        if value is not None:
            if value < 50:
                raise serializers.ValidationError("Height must be at least 50 cm.")
            if value > 300:
                raise serializers.ValidationError("Height must be at most 300 cm.")
        return value

    def validate_calorie_adjustment(self, value):
        """Validate calorie adjustment is within safe range"""
        if value < -1000:
            raise serializers.ValidationError("Calorie adjustment cannot be less than -1000 kcal.")
        if value > 1000:
            raise serializers.ValidationError("Calorie adjustment cannot be more than +1000 kcal.")
        return value

    def update(self, instance, validated_data):
        """Handle updating the user and profile instances."""
        user_data = validated_data.pop('user', {})
        
        # Track if key fields changed (requires recalculation)
        recalculation_fields = ['weight', 'height', 'date_of_birth', 'gender', 
                                'physical_activity', 'nutritional_goal', 
                                'calculation_method', 'calorie_adjustment']
        needs_recalculation = any(field in validated_data for field in recalculation_fields)
        
        # Update the Profile instance
        instance = super().update(instance, validated_data)
        
        # Update the related User instance
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        
        # Recalculate nutritional values if needed
        if needs_recalculation:
            instance.perform_calculations()

        return instance


class NutritionalCalculationsSerializer(serializers.Serializer):
    """Serializer for nutritional calculations response"""
    method = serializers.CharField()
    basic_data = serializers.DictField()
    calculations = serializers.DictField()
    saved_to_profile = serializers.BooleanField()