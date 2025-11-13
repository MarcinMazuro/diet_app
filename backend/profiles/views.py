from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer, NutritionalCalculationsSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the profile of the currently authenticated user."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


@api_view(['POST'])
def calculate_and_save_nutrition(request):
    """
    Calculate nutritional requirements and save them to the profile.
    This endpoint performs calculations and persists them to the database.
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    profile = request.user.profile
    
    # Check if all required data is present
    required_fields = {
        'weight': profile.weight,
        'height': profile.height,
        'date_of_birth': profile.date_of_birth,
        'gender': profile.gender,
        'physical_activity': profile.physical_activity,
        'nutritional_goal': profile.nutritional_goal
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value]
    
    if missing_fields:
        return Response(
            {
                'error': 'Missing required profile data',
                'missing_fields': missing_fields,
                'message': 'Please complete your profile before calculating nutritional requirements'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Perform calculations and save to database
    success = profile.perform_calculations()
    
    if not success:
        return Response(
            {'error': 'Failed to perform calculations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Refresh from database to get updated values
    profile.refresh_from_db()
    
    # Prepare response data
    age = profile.calculate_age()
    
    response_data = {
        'method': profile.get_calculation_method_display(),
        'basic_data': {
            'age': age,
            'weight': float(profile.weight),
            'height': float(profile.height),
            'bmi': float(profile.bmi) if profile.bmi else None,
            'gender': profile.get_gender_display(),
            'physical_activity': profile.get_physical_activity_display(),
            'nutritional_goal': profile.get_nutritional_goal_display(),
            'calorie_adjustment': profile.calorie_adjustment
        },
        'calculations': {
            'ppm': float(profile.ppm) if profile.ppm else None,
            'pal': profile.get_pal_value(),
            'cpm': float(profile.cpm) if profile.cpm else None,
            'recommended_daily_calories': float(profile.daily_calories) if profile.daily_calories else None,
            'macros': {
                'protein': float(profile.daily_protein) if profile.daily_protein else None,
                'carbohydrates': float(profile.daily_carbohydrates) if profile.daily_carbohydrates else None,
                'fat': float(profile.daily_fat) if profile.daily_fat else None
            }
        },
        'saved_to_profile': True,
        'last_updated': profile.calculations_last_updated
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_saved_calculations(request):
    """
    Get the last saved nutritional calculations from the profile.
    Does not perform new calculations.
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    profile = request.user.profile
    
    if not profile.daily_calories:
        return Response(
            {
                'message': 'No calculations available. Please use POST /calculate/ to perform calculations.',
                'has_calculations': False
            },
            status=status.HTTP_200_OK
        )
    
    age = profile.calculate_age()
    
    response_data = {
        'method': profile.get_calculation_method_display(),
        'basic_data': {
            'age': age,
            'weight': float(profile.weight) if profile.weight else None,
            'height': float(profile.height) if profile.height else None,
            'bmi': float(profile.bmi) if profile.bmi else None,
            'gender': profile.get_gender_display() if profile.gender else None,
            'physical_activity': profile.get_physical_activity_display() if profile.physical_activity else None,
            'nutritional_goal': profile.get_nutritional_goal_display() if profile.nutritional_goal else None,
            'calorie_adjustment': profile.calorie_adjustment
        },
        'calculations': {
            'ppm': float(profile.ppm) if profile.ppm else None,
            'pal': profile.get_pal_value() if profile.physical_activity else None,
            'cpm': float(profile.cpm) if profile.cpm else None,
            'recommended_daily_calories': float(profile.daily_calories) if profile.daily_calories else None,
            'macros': {
                'protein': float(profile.daily_protein) if profile.daily_protein else None,
                'carbohydrates': float(profile.daily_carbohydrates) if profile.daily_carbohydrates else None,
                'fat': float(profile.daily_fat) if profile.daily_fat else None
            }
        },
        'has_calculations': True,
        'last_updated': profile.calculations_last_updated
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
