from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileSerializer, CalculationRequestSerializer
from .services import NutritionService


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the profile of the currently authenticated user."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


@api_view(['POST'])
def calculate_and_save_nutrition(request):
    """Calculate nutritional requirements and save them to the profile."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    profile = request.user.profile
    
    # Validate request data
    serializer = CalculationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Perform calculations using service
    result = NutritionService.calculate_and_save(
        profile,
        calorie_adjustment=serializer.validated_data.get('calorie_adjustment'),
        custom_protein_pct=serializer.validated_data.get('custom_protein_percentage'),
        custom_carb_pct=serializer.validated_data.get('custom_carb_percentage'),
        custom_fat_pct=serializer.validated_data.get('custom_fat_percentage')
    )
    
    if not result.success:
        return Response({'error': result.error}, status=status.HTTP_400_BAD_REQUEST)
    
    # Refresh profile from database
    profile.refresh_from_db()
    
    response_data = result.to_response_dict(profile)
    response_data['saved_to_profile'] = True
    response_data['last_updated'] = profile.calculations_last_updated
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_saved_calculations(request):
    """Get the last saved nutritional calculations from the profile."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    profile = request.user.profile
    
    if not profile.daily_calories:
        return Response({
            'message': 'No calculations available. Please use POST /calculate/ to perform calculations.',
            'has_calculations': False
        }, status=status.HTTP_200_OK)
    
    # Build response from saved values
    from .services import AgeCalculator
    age = AgeCalculator.calculate(profile.date_of_birth)
    
    response_data = {
        'method': profile.get_calculation_method_display() if profile.calculation_method else None,
        'calorie_adjustment_used': profile.calorie_adjustment,
        'using_custom_macro_percentages': all([
            profile.custom_protein_percentage is not None,
            profile.custom_carb_percentage is not None,
            profile.custom_fat_percentage is not None
        ]),
        'basic_data': {
            'age': age,
            'weight': float(profile.weight) if profile.weight else None,
            'height': float(profile.height) if profile.height else None,
            'bmi': float(profile.bmi) if profile.bmi else None,
            'gender': profile.get_gender_display() if profile.gender else None,
            'physical_activity': profile.get_physical_activity_display() if profile.physical_activity else None,
            'nutritional_goal': profile.get_nutritional_goal_display() if profile.nutritional_goal else None
        },
        'calculations': {
            'ppm': float(profile.ppm) if profile.ppm else None,
            'cpm': float(profile.cpm) if profile.cpm else None,
            'recommended_daily_calories': float(profile.daily_calories) if profile.daily_calories else None,
            'macros': {
                'protein': {
                    'grams': float(profile.daily_protein) if profile.daily_protein else None,
                    'per_kg': float(profile.protein_per_kg) if profile.protein_per_kg else None,
                    'percentage': float(profile.protein_percentage) if profile.protein_percentage else None
                },
                'carbohydrates': {
                    'grams': float(profile.daily_carbohydrates) if profile.daily_carbohydrates else None,
                    'percentage': float(profile.carb_percentage) if profile.carb_percentage else None
                },
                'fat': {
                    'grams': float(profile.daily_fat) if profile.daily_fat else None,
                    'percentage': float(profile.fat_percentage) if profile.fat_percentage else None
                }
            }
        },
        'has_calculations': True,
        'last_updated': profile.calculations_last_updated
    }
    
    return Response(response_data, status=status.HTTP_200_OK)