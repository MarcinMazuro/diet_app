from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for profile owner"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    nutritional_goal_display = serializers.CharField(source='get_nutritional_goal_display', read_only=True)
    physical_activity_display = serializers.CharField(source='get_physical_activity_display', read_only=True)


    class Meta:
        model = Profile
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'gender', 'gender_display',
            'nutritional_goal', 'nutritional_goal_display',
            'physical_activity', 'physical_activity_display',
            'weight', 'height',
            'updated_at', 'date_joined'
        ]
        read_only_fields = [
            'username', 'email', 'updated_at', 'date_joined',
            'gender_display', 'nutritional_goal_display', 'physical_activity_display'
        ]


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')

        # Update Profile instance
        instance = super().update(instance, validated_data)

        # Update User instance
        user = instance.user
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        user.save()

        return instance
