from dataclasses import dataclass
from typing import Optional
from django.utils import timezone

from .calculators import (
    AgeCalculator,
    BMICalculator,
    BMRCalculator,
    MacroCalculator,
    BMRResult,
    MacroResult
)


@dataclass
class NutritionCalculationResult:
    """Complete result of nutrition calculations"""
    success: bool
    error: Optional[str] = None
    
    # Basic data
    age: Optional[int] = None
    bmi: Optional[float] = None
    
    # BMR results
    bmr: Optional[BMRResult] = None
    
    # Macro results
    macros: Optional[MacroResult] = None
    
    def to_response_dict(self, profile) -> dict:
        """Convert to API response dictionary"""
        if not self.success:
            return {'error': self.error}
        
        return {
            'method': profile.get_calculation_method_display(),
            'method_reason': self.bmr.method_reason,
            'calorie_adjustment_used': self.bmr.calorie_adjustment_used,
            'calorie_adjustment_source': self.bmr.calorie_adjustment_source,
            'using_custom_macro_percentages': self.macros.using_custom_percentages,
            'basic_data': {
                'age': self.age,
                'weight': float(profile.weight),
                'height': float(profile.height),
                'bmi': self.bmi,
                'gender': profile.get_gender_display(),
                'physical_activity': profile.get_physical_activity_display(),
                'nutritional_goal': profile.get_nutritional_goal_display()
            },
            'calculations': {
                'ppm': self.bmr.ppm,
                'pal': self.bmr.pal,
                'cpm': self.bmr.cpm,
                'recommended_daily_calories': self.bmr.daily_calories,
                'macros': {
                    'protein': {
                        'grams': self.macros.protein_grams,
                        'per_kg': self.macros.protein_per_kg,
                        'percentage': self.macros.protein_percentage
                    },
                    'carbohydrates': {
                        'grams': self.macros.carbohydrate_grams,
                        'percentage': self.macros.carb_percentage
                    },
                    'fat': {
                        'grams': self.macros.fat_grams,
                        'percentage': self.macros.fat_percentage
                    }
                }
            }
        }


class NutritionService:
    """Service for handling nutrition calculations"""
    
    REQUIRED_FIELDS = [
        'weight', 'height', 'date_of_birth',
        'gender', 'physical_activity', 'nutritional_goal'
    ]
    
    @classmethod
    def validate_profile(cls, profile) -> tuple[bool, list]:
        """
        Validate that profile has all required fields
        Returns: (is_valid, missing_fields)
        """
        missing = [
            field for field in cls.REQUIRED_FIELDS
            if not getattr(profile, field, None)
        ]
        return len(missing) == 0, missing
    
    @classmethod
    def calculate(
        cls,
        profile,
        calorie_adjustment: Optional[int] = None,
        custom_protein_pct: Optional[float] = None,
        custom_carb_pct: Optional[float] = None,
        custom_fat_pct: Optional[float] = None
    ) -> NutritionCalculationResult:
        """
        Perform all nutrition calculations for a profile
        """
        # Validate profile
        is_valid, missing_fields = cls.validate_profile(profile)
        if not is_valid:
            return NutritionCalculationResult(
                success=False,
                error=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Calculate age
        age = AgeCalculator.calculate(profile.date_of_birth)
        if not age:
            return NutritionCalculationResult(
                success=False,
                error="Could not calculate age from date of birth"
            )
        
        # Calculate BMI
        bmi = BMICalculator.calculate(profile.weight, profile.height)
        if not bmi:
            return NutritionCalculationResult(
                success=False,
                error="Could not calculate BMI"
            )
        
        # Calculate BMR/TDEE
        bmr_result = BMRCalculator.calculate_full(
            weight_kg=float(profile.weight),
            height_cm=float(profile.height),
            age=age,
            gender=profile.gender,
            physical_activity=profile.physical_activity,
            nutritional_goal=profile.nutritional_goal,
            bmi=bmi,
            calorie_adjustment=calorie_adjustment
        )
        
        if not bmr_result:
            return NutritionCalculationResult(
                success=False,
                error="Could not calculate metabolic rate"
            )
        
        # Calculate macros
        macro_result = MacroCalculator.calculate(
            calories=bmr_result.daily_calories,
            weight_kg=float(profile.weight),
            physical_activity=profile.physical_activity,
            nutritional_goal=profile.nutritional_goal,
            custom_protein_pct=custom_protein_pct,
            custom_carb_pct=custom_carb_pct,
            custom_fat_pct=custom_fat_pct
        )
        
        return NutritionCalculationResult(
            success=True,
            age=age,
            bmi=bmi,
            bmr=bmr_result,
            macros=macro_result
        )
    
    @classmethod
    def calculate_and_save(
        cls,
        profile,
        calorie_adjustment: Optional[int] = None,
        custom_protein_pct: Optional[float] = None,
        custom_carb_pct: Optional[float] = None,
        custom_fat_pct: Optional[float] = None
    ) -> NutritionCalculationResult:
        """
        Perform calculations and save results to profile
        """
        result = cls.calculate(
            profile,
            calorie_adjustment,
            custom_protein_pct,
            custom_carb_pct,
            custom_fat_pct
        )
        
        if not result.success:
            return result
        
        # Update profile with calculation parameters
        profile.calorie_adjustment = calorie_adjustment
        profile.custom_protein_percentage = custom_protein_pct
        profile.custom_carb_percentage = custom_carb_pct
        profile.custom_fat_percentage = custom_fat_pct
        
        # Save calculated values
        profile.bmi = result.bmi
        profile.calculation_method = result.bmr.method
        profile.ppm = result.bmr.ppm
        profile.cpm = result.bmr.cpm
        profile.daily_calories = result.bmr.daily_calories
        
        profile.daily_protein = result.macros.protein_grams
        profile.daily_carbohydrates = result.macros.carbohydrate_grams
        profile.daily_fat = result.macros.fat_grams
        profile.protein_per_kg = result.macros.protein_per_kg
        profile.protein_percentage = result.macros.protein_percentage
        profile.carb_percentage = result.macros.carb_percentage
        profile.fat_percentage = result.macros.fat_percentage
        
        profile.calculations_last_updated = timezone.now()
        
        profile.save(update_fields=[
            'calorie_adjustment',
            'custom_protein_percentage', 'custom_carb_percentage', 'custom_fat_percentage',
            'bmi', 'calculation_method', 'ppm', 'cpm', 'daily_calories',
            'daily_protein', 'daily_carbohydrates', 'daily_fat',
            'protein_per_kg', 'protein_percentage', 'carb_percentage', 'fat_percentage',
            'calculations_last_updated'
        ])
        
        return result