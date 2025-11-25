from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import Profile
from .services import (
    AgeCalculator, 
    BMICalculator, 
    BMRCalculator, 
    MacroCalculator,
    NutritionService
)
from .serializers import ProfileSerializer, CalculationRequestSerializer

User = get_user_model()


# =============================================================================
# CALCULATOR TESTS (Unit Tests)
# =============================================================================

class AgeCalculatorTests(TestCase):
    """Tests for AgeCalculator service"""
    
    def test_calculate_age_returns_correct_age(self):
        """Test that age is calculated correctly"""
        # Person born 30 years ago
        dob = date.today() - timedelta(days=30*365)
        age = AgeCalculator.calculate(dob)
        self.assertIn(age, [29, 30])  # Allow for leap years
    
    def test_calculate_age_with_birthday_today(self):
        """Test age calculation when birthday is today"""
        dob = date.today().replace(year=date.today().year - 25)
        age = AgeCalculator.calculate(dob)
        self.assertEqual(age, 25)
    
    def test_calculate_age_with_birthday_tomorrow(self):
        """Test age calculation when birthday is tomorrow (not yet had birthday)"""
        tomorrow = date.today() + timedelta(days=1)
        dob = tomorrow.replace(year=tomorrow.year - 25)
        age = AgeCalculator.calculate(dob)
        self.assertEqual(age, 24)  # Not yet 25
    
    def test_calculate_age_returns_none_for_none_input(self):
        """Test that None is returned for None input"""
        age = AgeCalculator.calculate(None)
        self.assertIsNone(age)


class BMICalculatorTests(TestCase):
    """Tests for BMICalculator service"""
    
    def test_calculate_bmi_normal_weight(self):
        """Test BMI calculation for normal weight person"""
        # 70 kg, 175 cm -> BMI ~22.86
        bmi = BMICalculator.calculate(Decimal('70'), Decimal('175'))
        self.assertAlmostEqual(bmi, 22.86, places=1)
    
    def test_calculate_bmi_overweight(self):
        """Test BMI calculation for overweight person"""
        # 90 kg, 175 cm -> BMI ~29.39
        bmi = BMICalculator.calculate(Decimal('90'), Decimal('175'))
        self.assertAlmostEqual(bmi, 29.39, places=1)
    
    def test_calculate_bmi_underweight(self):
        """Test BMI calculation for underweight person"""
        # 50 kg, 175 cm -> BMI ~16.33
        bmi = BMICalculator.calculate(Decimal('50'), Decimal('175'))
        self.assertAlmostEqual(bmi, 16.33, places=1)
    
    def test_calculate_bmi_returns_none_for_missing_data(self):
        """Test that None is returned when data is missing"""
        self.assertIsNone(BMICalculator.calculate(None, Decimal('175')))
        self.assertIsNone(BMICalculator.calculate(Decimal('70'), None))
        self.assertIsNone(BMICalculator.calculate(None, None))
    
    def test_get_category_underweight(self):
        """Test BMI category for underweight"""
        self.assertEqual(BMICalculator.get_category(17.0), "underweight")
    
    def test_get_category_normal(self):
        """Test BMI category for normal weight"""
        self.assertEqual(BMICalculator.get_category(22.0), "normal")
    
    def test_get_category_overweight(self):
        """Test BMI category for overweight"""
        self.assertEqual(BMICalculator.get_category(27.0), "overweight")
    
    def test_get_category_obese(self):
        """Test BMI category for obese"""
        self.assertEqual(BMICalculator.get_category(32.0), "obese")


class BMRCalculatorTests(TestCase):
    """Tests for BMRCalculator service"""
    
    def test_harris_benedict_male(self):
        """Test Harris-Benedict formula for male"""
        # 80 kg, 180 cm, 30 years old, male
        ppm = BMRCalculator.calculate_harris_benedict(80, 180, 30, 'M')
        self.assertIsNotNone(ppm)
        self.assertGreater(ppm, 1500)  # Should be reasonable for adult male
        self.assertLess(ppm, 2500)
    
    def test_harris_benedict_female(self):
        """Test Harris-Benedict formula for female"""
        # 60 kg, 165 cm, 30 years old, female
        ppm = BMRCalculator.calculate_harris_benedict(60, 165, 30, 'F')
        self.assertIsNotNone(ppm)
        self.assertGreater(ppm, 1200)  # Should be reasonable for adult female
        self.assertLess(ppm, 1800)
    
    def test_mifflin_male(self):
        """Test Mifflin-St Jeor formula for male"""
        # 80 kg, 180 cm, 30 years old, male
        ppm = BMRCalculator.calculate_mifflin(80, 180, 30, 'M')
        self.assertIsNotNone(ppm)
        self.assertGreater(ppm, 1500)
        self.assertLess(ppm, 2200)
    
    def test_mifflin_female(self):
        """Test Mifflin-St Jeor formula for female"""
        # 60 kg, 165 cm, 30 years old, female
        ppm = BMRCalculator.calculate_mifflin(60, 165, 30, 'F')
        self.assertIsNotNone(ppm)
        self.assertGreater(ppm, 1100)
        self.assertLess(ppm, 1600)
    
    def test_calculate_returns_none_for_missing_data(self):
        """Test that None is returned when data is missing"""
        self.assertIsNone(BMRCalculator.calculate_mifflin(None, 180, 30, 'M'))
        self.assertIsNone(BMRCalculator.calculate_harris_benedict(80, None, 30, 'M'))
    
    def test_get_pal_values(self):
        """Test PAL values for different activity levels"""
        self.assertEqual(BMRCalculator.get_pal('SEDENTARY'), 1.2)
        self.assertEqual(BMRCalculator.get_pal('LOW'), 1.45)
        self.assertEqual(BMRCalculator.get_pal('MODERATE'), 1.65)
        self.assertEqual(BMRCalculator.get_pal('HIGH'), 1.9)
        self.assertEqual(BMRCalculator.get_pal('VERY_HIGH'), 2.25)
    
    def test_calculate_tdee(self):
        """Test TDEE calculation"""
        ppm = 1800
        tdee = BMRCalculator.calculate_tdee(ppm, 'MODERATE')
        expected = 1800 * 1.65
        self.assertAlmostEqual(tdee, expected, places=1)
    
    def test_calculate_daily_calories_lose_weight(self):
        """Test daily calories calculation for weight loss"""
        cpm = 2500
        calories, adjustment, source = BMRCalculator.calculate_daily_calories(
            cpm, 'LOSE', 'M', None
        )
        self.assertEqual(adjustment, -500)
        self.assertEqual(source, "default")
        self.assertEqual(calories, 2000)
    
    def test_calculate_daily_calories_gain_weight(self):
        """Test daily calories calculation for weight gain"""
        cpm = 2500
        calories, adjustment, source = BMRCalculator.calculate_daily_calories(
            cpm, 'GAIN', 'M', None
        )
        self.assertEqual(adjustment, 500)
        self.assertEqual(source, "default")
        self.assertEqual(calories, 3000)
    
    def test_calculate_daily_calories_custom_adjustment(self):
        """Test daily calories with custom adjustment"""
        cpm = 2500
        calories, adjustment, source = BMRCalculator.calculate_daily_calories(
            cpm, 'LOSE', 'M', -300
        )
        self.assertEqual(adjustment, -300)
        self.assertEqual(source, "custom")
        self.assertEqual(calories, 2200)
    
    def test_minimum_calories_enforced_female(self):
        """Test that minimum calories are enforced for females"""
        cpm = 1500
        calories, _, _ = BMRCalculator.calculate_daily_calories(
            cpm, 'LOSE', 'F', -800  # Would go below minimum
        )
        self.assertEqual(calories, 1200)  # Minimum for female
    
    def test_minimum_calories_enforced_male(self):
        """Test that minimum calories are enforced for males"""
        cpm = 1800
        calories, _, _ = BMRCalculator.calculate_daily_calories(
            cpm, 'LOSE', 'M', -800  # Would go below minimum
        )
        self.assertEqual(calories, 1500)  # Minimum for male
    
    def test_get_recommended_method_normal_bmi(self):
        """Test that Harris-Benedict is recommended for normal BMI"""
        method, reason = BMRCalculator.get_recommended_method(22.0)
        self.assertEqual(method, 'HARRIS_BENEDICT')
        self.assertIn('Harris-Benedict', reason)
    
    def test_get_recommended_method_overweight_bmi(self):
        """Test that Mifflin is recommended for overweight BMI"""
        method, reason = BMRCalculator.get_recommended_method(27.0)
        self.assertEqual(method, 'MIFFLIN')
        self.assertIn('Mifflin', reason)


class MacroCalculatorTests(TestCase):
    """Tests for MacroCalculator service"""
    
    def test_calculate_automatic_lose_weight(self):
        """Test automatic macro calculation for weight loss"""
        result = MacroCalculator.calculate_automatic(
            calories=2000,
            weight_kg=80,
            physical_activity='MODERATE',
            nutritional_goal='LOSE'
        )
        
        self.assertFalse(result.using_custom_percentages)
        self.assertGreater(result.protein_grams, 0)
        self.assertGreater(result.carbohydrate_grams, 0)
        self.assertGreater(result.fat_grams, 0)
        
        # Percentages should sum to ~100
        total_pct = result.protein_percentage + result.carb_percentage + result.fat_percentage
        self.assertAlmostEqual(total_pct, 100, places=0)
    
    def test_calculate_with_custom_percentages(self):
        """Test macro calculation with custom percentages"""
        result = MacroCalculator.calculate_with_custom_percentages(
            calories=2000,
            weight_kg=80,
            protein_pct=0.3,
            carb_pct=0.5,
            fat_pct=0.2
        )
        
        self.assertTrue(result.using_custom_percentages)
        self.assertAlmostEqual(result.protein_percentage, 30, places=0)
        self.assertAlmostEqual(result.carb_percentage, 50, places=0)
        self.assertAlmostEqual(result.fat_percentage, 20, places=0)
        
        # Verify grams calculation
        # Protein: 2000 * 0.3 / 4 = 150g
        self.assertAlmostEqual(result.protein_grams, 150, places=0)
        # Carbs: 2000 * 0.5 / 4 = 250g
        self.assertAlmostEqual(result.carbohydrate_grams, 250, places=0)
        # Fat: 2000 * 0.2 / 9 = ~44.4g
        self.assertAlmostEqual(result.fat_grams, 44.4, places=0)
    
    def test_calculate_normalizes_percentages(self):
        """Test that percentages are normalized if they don't sum to 1"""
        result = MacroCalculator.calculate_with_custom_percentages(
            calories=2000,
            weight_kg=80,
            protein_pct=0.3,
            carb_pct=0.5,
            fat_pct=0.3  # Sum = 1.1, should be normalized
        )
        
        # Percentages should still sum to 100 after normalization
        total_pct = result.protein_percentage + result.carb_percentage + result.fat_percentage
        self.assertAlmostEqual(total_pct, 100, places=0)
    
    def test_protein_per_kg_increases_with_activity(self):
        """Test that protein per kg increases with higher activity"""
        result_sedentary = MacroCalculator.calculate_automatic(
            calories=2500, weight_kg=80, physical_activity='SEDENTARY', nutritional_goal='MAINTAIN'
        )
        result_very_high = MacroCalculator.calculate_automatic(
            calories=2500, weight_kg=80, physical_activity='VERY_HIGH', nutritional_goal='MAINTAIN'
        )
        
        self.assertGreater(result_very_high.protein_per_kg, result_sedentary.protein_per_kg)


# =============================================================================
# NUTRITION SERVICE TESTS (Integration Tests)
# =============================================================================

class NutritionServiceTests(TestCase):
    """Tests for NutritionService"""
    
    def setUp(self):
        """Set up test user and profile"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
        
        # Set complete profile data
        self.profile.weight = Decimal('80.00')
        self.profile.height = Decimal('180.00')
        self.profile.date_of_birth = date(1990, 1, 15)
        self.profile.gender = 'M'
        self.profile.physical_activity = 'MODERATE'
        self.profile.nutritional_goal = 'MAINTAIN'
        self.profile.save()
    
    def test_validate_profile_with_complete_data(self):
        """Test profile validation passes with complete data"""
        is_valid, missing = NutritionService.validate_profile(self.profile)
        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
    
    def test_validate_profile_with_missing_data(self):
        """Test profile validation fails with missing data"""
        self.profile.weight = None
        self.profile.save()
        
        is_valid, missing = NutritionService.validate_profile(self.profile)
        self.assertFalse(is_valid)
        self.assertIn('weight', missing)
    
    def test_calculate_returns_success(self):
        """Test successful calculation"""
        result = NutritionService.calculate(self.profile)
        
        self.assertTrue(result.success)
        self.assertIsNone(result.error)
        self.assertIsNotNone(result.age)
        self.assertIsNotNone(result.bmi)
        self.assertIsNotNone(result.bmr)
        self.assertIsNotNone(result.macros)
    
    def test_calculate_fails_with_missing_data(self):
        """Test calculation fails with missing data"""
        self.profile.weight = None
        self.profile.save()
        
        result = NutritionService.calculate(self.profile)
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_calculate_with_custom_calorie_adjustment(self):
        """Test calculation with custom calorie adjustment"""
        result = NutritionService.calculate(self.profile, calorie_adjustment=-300)
        
        self.assertTrue(result.success)
        self.assertEqual(result.bmr.calorie_adjustment_used, -300)
        self.assertEqual(result.bmr.calorie_adjustment_source, "custom")
    
    def test_calculate_with_custom_macro_percentages(self):
        """Test calculation with custom macro percentages"""
        result = NutritionService.calculate(
            self.profile,
            custom_protein_pct=0.35,
            custom_carb_pct=0.45,
            custom_fat_pct=0.20
        )
        
        self.assertTrue(result.success)
        self.assertTrue(result.macros.using_custom_percentages)
        self.assertAlmostEqual(result.macros.protein_percentage, 35, places=0)
    
    def test_calculate_and_save_stores_values(self):
        """Test that calculate_and_save stores values in database"""
        result = NutritionService.calculate_and_save(self.profile)
        
        self.assertTrue(result.success)
        
        # Refresh from database
        self.profile.refresh_from_db()
        
        self.assertIsNotNone(self.profile.bmi)
        self.assertIsNotNone(self.profile.ppm)
        self.assertIsNotNone(self.profile.cpm)
        self.assertIsNotNone(self.profile.daily_calories)
        self.assertIsNotNone(self.profile.daily_protein)
        self.assertIsNotNone(self.profile.daily_carbohydrates)
        self.assertIsNotNone(self.profile.daily_fat)
        self.assertIsNotNone(self.profile.calculations_last_updated)


# =============================================================================
# SERIALIZER TESTS
# =============================================================================

class ProfileSerializerTests(TestCase):
    """Tests for ProfileSerializer"""
    
    def setUp(self):
        """Set up test user and profile"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
    
    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""
        serializer = ProfileSerializer(instance=self.profile)
        expected_fields = [
            'username', 'email', 'first_name', 'last_name',
            'gender', 'gender_display',
            'nutritional_goal', 'nutritional_goal_display',
            'physical_activity', 'physical_activity_display',
            'weight', 'height', 'date_of_birth', 'age'
        ]
        for field in expected_fields:
            self.assertIn(field, serializer.data)
    
    def test_validate_date_of_birth_too_young(self):
        """Test validation rejects users under 13"""
        serializer = ProfileSerializer(data={
            'date_of_birth': date.today() - timedelta(days=10*365)  # 10 years old
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('date_of_birth', serializer.errors)
    
    def test_validate_date_of_birth_future(self):
        """Test validation rejects future dates"""
        serializer = ProfileSerializer(data={
            'date_of_birth': date.today() + timedelta(days=1)
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('date_of_birth', serializer.errors)
    
    def test_validate_weight_too_low(self):
        """Test validation rejects weight below 20 kg"""
        serializer = ProfileSerializer(data={'weight': 15}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('weight', serializer.errors)
    
    def test_validate_weight_too_high(self):
        """Test validation rejects weight above 500 kg"""
        serializer = ProfileSerializer(data={'weight': 600}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('weight', serializer.errors)
    
    def test_validate_height_too_low(self):
        """Test validation rejects height below 50 cm"""
        serializer = ProfileSerializer(data={'height': 40}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('height', serializer.errors)
    
    def test_validate_height_too_high(self):
        """Test validation rejects height above 300 cm"""
        serializer = ProfileSerializer(data={'height': 350}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('height', serializer.errors)
    
    def test_validate_custom_macros_partial_fails(self):
        """Test validation fails when only some macro percentages are provided"""
        serializer = ProfileSerializer(data={
            'custom_protein_percentage': 0.3,
            'custom_carb_percentage': 0.5,
            # Missing fat percentage
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_validate_custom_macros_invalid_sum(self):
        """Test validation fails when macro percentages don't sum to 1.0"""
        serializer = ProfileSerializer(data={
            'custom_protein_percentage': 0.3,
            'custom_carb_percentage': 0.5,
            'custom_fat_percentage': 0.4,  # Sum = 1.2
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_validate_custom_macros_valid_sum(self):
        """Test validation passes when macro percentages sum to 1.0"""
        serializer = ProfileSerializer(data={
            'custom_protein_percentage': 0.3,
            'custom_carb_percentage': 0.5,
            'custom_fat_percentage': 0.2,  # Sum = 1.0
        }, partial=True)
        self.assertTrue(serializer.is_valid())


class CalculationRequestSerializerTests(TestCase):
    """Tests for CalculationRequestSerializer"""
    
    def test_valid_calorie_adjustment(self):
        """Test valid calorie adjustment"""
        serializer = CalculationRequestSerializer(data={'calorie_adjustment': -300})
        self.assertTrue(serializer.is_valid())
    
    def test_calorie_adjustment_too_low(self):
        """Test calorie adjustment below -1000 fails"""
        serializer = CalculationRequestSerializer(data={'calorie_adjustment': -1500})
        self.assertFalse(serializer.is_valid())
    
    def test_calorie_adjustment_too_high(self):
        """Test calorie adjustment above 1000 fails"""
        serializer = CalculationRequestSerializer(data={'calorie_adjustment': 1500})
        self.assertFalse(serializer.is_valid())
    
    def test_valid_custom_macros(self):
        """Test valid custom macro percentages"""
        serializer = CalculationRequestSerializer(data={
            'custom_protein_percentage': 0.3,
            'custom_carb_percentage': 0.5,
            'custom_fat_percentage': 0.2,
        })
        self.assertTrue(serializer.is_valid())
    
    def test_partial_macros_fails(self):
        """Test partial macro percentages fail"""
        serializer = CalculationRequestSerializer(data={
            'custom_protein_percentage': 0.3,
            'custom_carb_percentage': 0.5,
        })
        self.assertFalse(serializer.is_valid())


# =============================================================================
# API VIEW TESTS (Integration Tests)
# =============================================================================

class ProfileAPITests(APITestCase):
    """Tests for Profile API endpoints"""
    
    def setUp(self):
        """Set up test user and client"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Set up complete profile
        self.profile = self.user.profile
        self.profile.weight = Decimal('80.00')
        self.profile.height = Decimal('180.00')
        self.profile.date_of_birth = date(1990, 1, 15)
        self.profile.gender = 'M'
        self.profile.physical_activity = 'MODERATE'
        self.profile.nutritional_goal = 'MAINTAIN'
        self.profile.save()
    
    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated"""
        response = self.client.get('/api/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile when not authenticated"""
        self.client.logout()
        response = self.client.get('/api/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Test updating profile"""
        response = self.client.patch('/api/profiles/me/', {
            'weight': 85,
            'height': 182
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.weight), 85)
        self.assertEqual(float(self.profile.height), 182)
    
    def test_update_profile_invalid_weight(self):
        """Test updating profile with invalid weight"""
        response = self.client.patch('/api/profiles/me/', {'weight': 10})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', response.data)


class CalculationAPITests(APITestCase):
    """Tests for Calculation API endpoints"""
    
    def setUp(self):
        """Set up test user and client"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Set up complete profile
        self.profile = self.user.profile
        self.profile.weight = Decimal('80.00')
        self.profile.height = Decimal('180.00')
        self.profile.date_of_birth = date(1990, 1, 15)
        self.profile.gender = 'M'
        self.profile.physical_activity = 'MODERATE'
        self.profile.nutritional_goal = 'MAINTAIN'
        self.profile.save()
    
    def test_calculate_nutrition_success(self):
        """Test successful nutrition calculation"""
        response = self.client.post('/api/profiles/calculate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('calculations', response.data)
        self.assertIn('basic_data', response.data)
        self.assertTrue(response.data['saved_to_profile'])
    
    def test_calculate_nutrition_with_calorie_adjustment(self):
        """Test calculation with custom calorie adjustment"""
        response = self.client.post('/api/profiles/calculate/', {
            'calorie_adjustment': -300
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['calorie_adjustment_used'], -300)
        self.assertEqual(response.data['calorie_adjustment_source'], 'custom')
    
    def test_calculate_nutrition_with_custom_macros(self):
        """Test calculation with custom macro percentages"""
        response = self.client.post('/api/profiles/calculate/', {
            'custom_protein_percentage': '0.35',
            'custom_carb_percentage': '0.45',
            'custom_fat_percentage': '0.20'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['using_custom_macro_percentages'])
        self.assertAlmostEqual(
            response.data['calculations']['macros']['protein']['percentage'], 
            35, 
            places=0
        )
    
    def test_calculate_nutrition_missing_profile_data(self):
        """Test calculation fails with incomplete profile"""
        self.profile.weight = None
        self.profile.save()
        
        response = self.client.post('/api/profiles/calculate/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_calculate_nutrition_unauthenticated(self):
        """Test calculation fails when not authenticated"""
        self.client.logout()
        response = self.client.post('/api/profiles/calculate/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_saved_calculations_success(self):
        """Test getting saved calculations"""
        # First, perform calculation
        self.client.post('/api/profiles/calculate/')
        
        # Then, get saved calculations
        response = self.client.get('/api/profiles/calculations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_calculations'])
        self.assertIn('calculations', response.data)
    
    def test_get_saved_calculations_no_calculations(self):
        """Test getting calculations when none exist"""
        response = self.client.get('/api/profiles/calculations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_calculations'])
        self.assertIn('message', response.data)
    
    def test_get_saved_calculations_unauthenticated(self):
        """Test getting calculations fails when not authenticated"""
        self.client.logout()
        response = self.client.get('/api/profiles/calculations/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# =============================================================================
# MODEL TESTS
# =============================================================================

class ProfileModelTests(TestCase):
    """Tests for Profile model"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
    
    def test_profile_created_with_user(self):
        """Test that profile is automatically created when user is created"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertIsInstance(new_user.profile, Profile)
    
    def test_profile_str_representation(self):
        """Test profile string representation"""
        self.assertEqual(str(self.profile), 'Profile of testuser')
    
    def test_gender_choices(self):
        """Test gender choices are valid"""
        valid_genders = ['M', 'F', 'O']
        for gender in valid_genders:
            self.profile.gender = gender
            self.profile.full_clean()  # Should not raise
    
    def test_nutritional_goal_choices(self):
        """Test nutritional goal choices are valid"""
        valid_goals = ['LOSE', 'MAINTAIN', 'GAIN']
        for goal in valid_goals:
            self.profile.nutritional_goal = goal
            self.profile.full_clean()  # Should not raise
    
    def test_physical_activity_choices(self):
        """Test physical activity choices are valid"""
        valid_activities = ['SEDENTARY', 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH']
        for activity in valid_activities:
            self.profile.physical_activity = activity
            self.profile.full_clean()  # Should not raise
