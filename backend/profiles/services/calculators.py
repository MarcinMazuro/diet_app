from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import date


@dataclass
class MacroResult:
    """Result of macro calculations"""
    protein_grams: float
    carbohydrate_grams: float
    fat_grams: float
    protein_per_kg: float
    protein_percentage: float
    carb_percentage: float
    fat_percentage: float
    using_custom_percentages: bool


@dataclass
class BMRResult:
    """Result of BMR/metabolic calculations"""
    ppm: float  # Basal Metabolic Rate
    pal: float  # Physical Activity Level
    cpm: float  # Total Daily Energy Expenditure
    daily_calories: float  # Adjusted for goal
    method: str
    method_reason: str
    calorie_adjustment_used: int
    calorie_adjustment_source: str


class AgeCalculator:
    """Calculate age from date of birth"""
    
    @staticmethod
    def calculate(date_of_birth: date) -> Optional[int]:
        if not date_of_birth:
            return None
        today = date.today()
        age = today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )
        return age


class BMICalculator:
    """Calculate Body Mass Index"""
    
    @staticmethod
    def calculate(weight_kg: Decimal, height_cm: Decimal) -> Optional[float]:
        if not weight_kg or not height_cm:
            return None
        height_m = float(height_cm) / 100
        bmi = float(weight_kg) / (height_m ** 2)
        return round(bmi, 2)
    
    @staticmethod
    def get_category(bmi: float) -> str:
        """Get BMI category"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"


class BMRCalculator:
    """Calculate Basal Metabolic Rate using different formulas"""
    
    # Physical Activity Level multipliers
    PAL_VALUES = {
        'SEDENTARY': 1.2,
        'LOW': 1.45,
        'MODERATE': 1.65,
        'HIGH': 1.9,
        'VERY_HIGH': 2.25,
    }
    
    # Default calorie adjustments by goal
    DEFAULT_ADJUSTMENTS = {
        'LOSE': -500,
        'GAIN': 500,
        'MAINTAIN': 0
    }
    
    # Minimum safe calories
    MIN_CALORIES = {
        'M': 1500,
        'F': 1200,
        'default': 1350
    }
    
    @classmethod
    def calculate_harris_benedict(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str
    ) -> Optional[float]:
        """
        Harris-Benedict formula
        Women: PPM = 655.1 + (9.563 x weight) + (1.85 x height) - (4.676 x age)
        Men: PPM = 66.5 + (13.75 x weight) + (5.003 x height) - (6.775 x age)
        """
        if not all([weight_kg, height_cm, age, gender]):
            return None
        
        if gender == 'F':
            ppm = 655.1 + (9.563 * weight_kg) + (1.85 * height_cm) - (4.676 * age)
        elif gender == 'M':
            ppm = 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.775 * age)
        else:
            # Average for other genders
            ppm_f = 655.1 + (9.563 * weight_kg) + (1.85 * height_cm) - (4.676 * age)
            ppm_m = 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.775 * age)
            ppm = (ppm_f + ppm_m) / 2
        
        return round(ppm, 2)
    
    @classmethod
    def calculate_mifflin(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str
    ) -> Optional[float]:
        """
        Mifflin-St Jeor formula
        Women: PPM = (10 x weight) + (6.25 x height) - (5 x age) - 161
        Men: PPM = (10 x weight) + (6.25 x height) - (5 x age) + 5
        """
        if not all([weight_kg, height_cm, age, gender]):
            return None
        
        base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
        
        if gender == 'F':
            ppm = base - 161
        elif gender == 'M':
            ppm = base + 5
        else:
            ppm = base - 78  # Average
        
        return round(ppm, 2)
    
    @classmethod
    def get_recommended_method(cls, bmi: float) -> tuple[str, str]:
        """
        Get recommended calculation method based on BMI
        Returns: (method_code, reason)
        """
        if bmi >= 25:
            return (
                'MIFFLIN',
                f"Mifflin-St Jeor selected (BMI: {bmi:.1f} - recommended for overweight individuals)"
            )
        else:
            return (
                'HARRIS_BENEDICT',
                f"Harris-Benedict selected (BMI: {bmi:.1f} - recommended for normal weight, active individuals)"
            )
    
    @classmethod
    def get_pal(cls, physical_activity: str) -> float:
        """Get Physical Activity Level multiplier"""
        return cls.PAL_VALUES.get(physical_activity, 1.2)
    
    @classmethod
    def calculate_tdee(cls, ppm: float, physical_activity: str) -> float:
        """Calculate Total Daily Energy Expenditure (CPM)"""
        pal = cls.get_pal(physical_activity)
        return round(ppm * pal, 2)
    
    @classmethod
    def calculate_daily_calories(
        cls,
        cpm: float,
        nutritional_goal: str,
        gender: str,
        calorie_adjustment: Optional[int] = None
    ) -> tuple[float, int, str]:
        """
        Calculate recommended daily calories
        Returns: (calories, adjustment_used, adjustment_source)
        """
        if calorie_adjustment is None:
            adjustment = cls.DEFAULT_ADJUSTMENTS.get(nutritional_goal, 0)
            source = "default"
        else:
            adjustment = calorie_adjustment
            source = "custom"
        
        calories = cpm + adjustment
        
        # Ensure minimum safe calories
        min_cal = cls.MIN_CALORIES.get(gender, cls.MIN_CALORIES['default'])
        calories = max(calories, min_cal)
        
        return round(calories, 2), adjustment, source
    
    @classmethod
    def calculate_full(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        physical_activity: str,
        nutritional_goal: str,
        bmi: float,
        calorie_adjustment: Optional[int] = None
    ) -> Optional[BMRResult]:
        """Perform full BMR/TDEE calculation"""
        
        method, method_reason = cls.get_recommended_method(bmi)
        
        # Calculate PPM based on method
        if method == 'HARRIS_BENEDICT':
            ppm = cls.calculate_harris_benedict(weight_kg, height_cm, age, gender)
        else:
            ppm = cls.calculate_mifflin(weight_kg, height_cm, age, gender)
        
        if not ppm:
            return None
        
        pal = cls.get_pal(physical_activity)
        cpm = cls.calculate_tdee(ppm, physical_activity)
        daily_calories, adj_used, adj_source = cls.calculate_daily_calories(
            cpm, nutritional_goal, gender, calorie_adjustment
        )
        
        return BMRResult(
            ppm=ppm,
            pal=pal,
            cpm=cpm,
            daily_calories=daily_calories,
            method=method,
            method_reason=method_reason,
            calorie_adjustment_used=adj_used,
            calorie_adjustment_source=adj_source
        )


class MacroCalculator:
    """Calculate macronutrient distribution"""
    
    # Protein per kg based on activity level and goal
    PROTEIN_PER_KG = {
        'LOSE': {
            'SEDENTARY': 1.6,
            'LOW': 1.8,
            'MODERATE': 2.0,
            'HIGH': 2.2,
            'VERY_HIGH': 2.4,
        },
        'GAIN': {
            'SEDENTARY': 1.4,
            'LOW': 1.6,
            'MODERATE': 1.8,
            'HIGH': 2.0,
            'VERY_HIGH': 2.2,
        },
        'MAINTAIN': {
            'SEDENTARY': 1.2,
            'LOW': 1.4,
            'MODERATE': 1.6,
            'HIGH': 1.8,
            'VERY_HIGH': 2.0,
        }
    }
    
    # Fat/Carb split for remaining calories (after protein)
    FAT_CARB_SPLIT = {
        'LOSE': {
            'high_activity': {'fat': 0.25, 'carb': 0.75},
            'low_activity': {'fat': 0.35, 'carb': 0.65}
        },
        'GAIN': {
            'high_activity': {'fat': 0.20, 'carb': 0.80},
            'low_activity': {'fat': 0.25, 'carb': 0.75}
        },
        'MAINTAIN': {
            'high_activity': {'fat': 0.25, 'carb': 0.75},
            'low_activity': {'fat': 0.30, 'carb': 0.70}
        }
    }
    
    HIGH_ACTIVITY_LEVELS = ['HIGH', 'VERY_HIGH']
    
    @classmethod
    def calculate_with_custom_percentages(
        cls,
        calories: float,
        weight_kg: float,
        protein_pct: float,
        carb_pct: float,
        fat_pct: float
    ) -> MacroResult:
        """Calculate macros using custom percentages"""
        
        # Normalize if needed
        total = protein_pct + carb_pct + fat_pct
        if abs(total - 1.0) > 0.01:
            protein_pct /= total
            carb_pct /= total
            fat_pct /= total
        
        protein_cal = calories * protein_pct
        carb_cal = calories * carb_pct
        fat_cal = calories * fat_pct
        
        protein_grams = protein_cal / 4
        carb_grams = carb_cal / 4
        fat_grams = fat_cal / 9
        
        return MacroResult(
            protein_grams=round(protein_grams, 1),
            carbohydrate_grams=round(carb_grams, 1),
            fat_grams=round(fat_grams, 1),
            protein_per_kg=round(protein_grams / weight_kg, 2),
            protein_percentage=round(protein_pct * 100, 1),
            carb_percentage=round(carb_pct * 100, 1),
            fat_percentage=round(fat_pct * 100, 1),
            using_custom_percentages=True
        )
    
    @classmethod
    def calculate_automatic(
        cls,
        calories: float,
        weight_kg: float,
        physical_activity: str,
        nutritional_goal: str
    ) -> MacroResult:
        """Calculate macros automatically based on activity and goal"""
        
        # Get protein per kg
        goal_protein = cls.PROTEIN_PER_KG.get(nutritional_goal, cls.PROTEIN_PER_KG['MAINTAIN'])
        protein_per_kg = goal_protein.get(physical_activity, 1.6)
        
        protein_grams = weight_kg * protein_per_kg
        protein_cal = protein_grams * 4
        
        # Remaining calories for fat and carbs
        remaining_cal = calories - protein_cal
        
        # Get fat/carb split
        activity_type = 'high_activity' if physical_activity in cls.HIGH_ACTIVITY_LEVELS else 'low_activity'
        split = cls.FAT_CARB_SPLIT.get(nutritional_goal, cls.FAT_CARB_SPLIT['MAINTAIN'])[activity_type]
        
        fat_cal = remaining_cal * split['fat']
        carb_cal = remaining_cal * split['carb']
        
        fat_grams = fat_cal / 9
        carb_grams = carb_cal / 4
        
        return MacroResult(
            protein_grams=round(protein_grams, 1),
            carbohydrate_grams=round(carb_grams, 1),
            fat_grams=round(fat_grams, 1),
            protein_per_kg=round(protein_per_kg, 2),
            protein_percentage=round((protein_cal / calories) * 100, 1),
            carb_percentage=round((carb_cal / calories) * 100, 1),
            fat_percentage=round((fat_cal / calories) * 100, 1),
            using_custom_percentages=False
        )
    
    @classmethod
    def calculate(
        cls,
        calories: float,
        weight_kg: float,
        physical_activity: str,
        nutritional_goal: str,
        custom_protein_pct: Optional[float] = None,
        custom_carb_pct: Optional[float] = None,
        custom_fat_pct: Optional[float] = None
    ) -> MacroResult:
        """Calculate macros - uses custom if all provided, otherwise automatic"""
        
        has_custom = all([
            custom_protein_pct is not None,
            custom_carb_pct is not None,
            custom_fat_pct is not None
        ])
        
        if has_custom:
            return cls.calculate_with_custom_percentages(
                calories, weight_kg,
                float(custom_protein_pct),
                float(custom_carb_pct),
                float(custom_fat_pct)
            )
        else:
            return cls.calculate_automatic(
                calories, weight_kg, physical_activity, nutritional_goal
            )
        