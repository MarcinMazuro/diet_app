from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        TRANSGENDER = 'T', 'Transgender'
        NON_BINARY = 'NB', 'Non-binary'
        AGENDER = 'AG', 'Agender'
        GENDERFLUID = 'GF', 'Genderfluid'
        BIGENDER = 'BI', 'Bigender'
        PANGENDER = 'PAN', 'Pangender'
        GENDERQUEER = 'GQ', 'Genderqueer'
        DEMIBOY = 'DB', 'Demiboy'
        DEMIGIRL = 'DG', 'Demigirl'
        ANDROGYNE = 'AN', 'Androgyne'
        NEUTROIS = 'NE', 'Neutrois'
        TRIGENDER = 'TRI', 'Trigender'
        GENDERFLUX = 'GX', 'Genderflux'
        XENOGENDER = 'XE', 'Xenogender'
        TWO_SPIRIT = '2S', 'Two-Spirit'
        ALIAGENDER = 'AL', 'Aliagender'
        GRAYGENDER = 'GG', 'Graygender'
        POLYPENDER = 'PO', 'Polygender'
        HELIKOPTER_BOJOWY = "HB", 'Helboj'
        OTHER = 'O', 'Other'

    class NutritionalGoal(models.TextChoices):
        LOSE_WEIGHT = 'LOSE', 'Lose Weight'
        MAINTAIN_WEIGHT = 'MAINTAIN', 'Maintain Weight'
        GAIN_WEIGHT = 'GAIN', 'Gain Weight'

    class PhysicalActivity(models.TextChoices):
        # Updated to match the image (PAL values)
        SEDENTARY = 'SEDENTARY', 'Lying down, no movement (PAL: 1.2)'
        LOW = 'LOW', 'Low activity (office work, little movement) (PAL: 1.4-1.5)'
        MODERATE = 'MODERATE', 'Moderate activity (light work + recreational movement) (PAL: 1.6-1.7)'
        HIGH = 'HIGH', 'High activity (physical work, regular sport) (PAL: 1.8-2.0)'
        VERY_HIGH = 'VERY_HIGH', 'Very high activity (athlete, heavy work) (PAL: 2.1-2.4)'

    class CalculationMethod(models.TextChoices):
        MIFFLIN = 'MIFFLIN', 'Mifflin-St Jeor'
        HARRIS_BENEDICT = 'HARRIS_BENEDICT', 'Harris-Benedict'

    # Basic user data
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Physical characteristics
    gender = models.CharField(
        max_length=3,
        choices=Gender.choices,
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="Date of birth for age calculation"
    )
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(500)],
        help_text="Weight in kilograms (20-500 kg)"
    )
    height = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        help_text="Height in centimeters (50-300 cm)"
    )
    
    # Activity and goals
    nutritional_goal = models.CharField(
        max_length=10,
        choices=NutritionalGoal.choices,
        null=True,
        blank=True
    )
    physical_activity = models.CharField(
        max_length=10,
        choices=PhysicalActivity.choices,
        null=True,
        blank=True
    )
    
    # Calculation preferences
    calculation_method = models.CharField(
        max_length=20,
        choices=CalculationMethod.choices,
        default=CalculationMethod.MIFFLIN,
        help_text="Method used for calculating daily calorie needs"
    )
    calorie_adjustment = models.IntegerField(
        default=0,
        validators=[MinValueValidator(-1000), MaxValueValidator(1000)],
        help_text="Manual calorie adjustment (-1000 to +1000 kcal)"
    )
    
    # Calculated and stored values (updated when calculate() is called)
    bmi = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Body Mass Index"
    )
    ppm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Basal Metabolic Rate (PPM)"
    )
    cpm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total Daily Energy Expenditure (CPM)"
    )
    daily_calories = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Recommended daily calories (with goal adjustment)"
    )
    daily_protein = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Recommended daily protein in grams"
    )
    daily_carbohydrates = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Recommended daily carbohydrates in grams"
    )
    daily_fat = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Recommended daily fat in grams"
    )
    
    # Timestamps
    calculations_last_updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time nutritional calculations were performed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        return age
    
    def calculate_bmi(self):
        """Calculate BMI (Body Mass Index)"""
        if not self.weight or not self.height:
            return None
        height_in_meters = float(self.height) / 100
        bmi = float(self.weight) / (height_in_meters ** 2)
        return round(bmi, 2)
    
    def calculate_ppm_harris_benedict(self):
        """
        Calculate PPM using Harris-Benedict formula
        For women: PPM = 655.1 + (9.563 x weight[kg]) + (1.85 x height[cm]) - (4.676 x age)
        For men: PPM = 66.5 + (13.75 x weight[kg]) + (5.003 x height[cm]) - (6.775 x age)
        """
        age = self.calculate_age()
        if not all([self.weight, self.height, age, self.gender]):
            return None
        
        weight = float(self.weight)
        height = float(self.height)
        
        if self.gender == self.Gender.FEMALE:
            ppm = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)
        elif self.gender == self.Gender.MALE:
            ppm = 66.5 + (13.75 * weight) + (5.003 * height) - (6.775 * age)
        else:
            # Average for other genders
            ppm_female = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)
            ppm_male = 66.5 + (13.75 * weight) + (5.003 * height) - (6.775 * age)
            ppm = (ppm_female + ppm_male) / 2
        
        return round(ppm, 2)
    
    def calculate_ppm_mifflin(self):
        """
        Calculate PPM using Mifflin-St Jeor formula
        For women: PPM = (10 x weight[kg]) + (6.25 x height[cm]) - (5 x age) - 161
        For men: PPM = (10 x weight[kg]) + (6.25 x height[cm]) - (5 x age) + 5
        """
        age = self.calculate_age()
        if not all([self.weight, self.height, age, self.gender]):
            return None
        
        weight = float(self.weight)
        height = float(self.height)
        
        base = (10 * weight) + (6.25 * height) - (5 * age)
        
        if self.gender == self.Gender.FEMALE:
            ppm = base - 161
        elif self.gender == self.Gender.MALE:
            ppm = base + 5
        else:
            # Average for other genders
            ppm = base - 78
        
        return round(ppm, 2)
    
    def get_pal_value(self):
        """Get PAL (Physical Activity Level) multiplier based on the image"""
        pal_values = {
            self.PhysicalActivity.SEDENTARY: 1.2,      # Lying down, no movement
            self.PhysicalActivity.LOW: 1.45,           # Low activity (average of 1.4-1.5)
            self.PhysicalActivity.MODERATE: 1.65,      # Moderate activity (average of 1.6-1.7)
            self.PhysicalActivity.HIGH: 1.9,           # High activity (average of 1.8-2.0)
            self.PhysicalActivity.VERY_HIGH: 2.25,     # Very high activity (average of 2.1-2.4)
        }
        return pal_values.get(self.physical_activity, 1.2)

    def calculate_cpm(self):
        """
        Calculate CPM (Total Daily Energy Expenditure)
        CPM = PPM * PAL
        """
        if self.calculation_method == self.CalculationMethod.HARRIS_BENEDICT:
            ppm = self.calculate_ppm_harris_benedict()
        else:  # default to mifflin
            ppm = self.calculate_ppm_mifflin()
        
        if not ppm or not self.physical_activity:
            return None
        
        pal = self.get_pal_value()
        cpm = ppm * pal
        
        return round(cpm, 2)

    def calculate_daily_calories(self):
        """
        Calculate recommended daily calories based on nutritional goal
        Includes user's manual calorie adjustment
        """
        cpm = self.calculate_cpm()
        if not cpm or not self.nutritional_goal:
            return None
        
        # Base calorie adjustment based on goal
        if self.nutritional_goal == self.NutritionalGoal.LOSE_WEIGHT:
            calories = cpm - 500  # 500 calorie deficit
        elif self.nutritional_goal == self.NutritionalGoal.GAIN_WEIGHT:
            calories = cpm + 500  # 500 calorie surplus
        else:  # MAINTAIN_WEIGHT
            calories = cpm
        
        # Add user's manual adjustment
        calories += self.calorie_adjustment
        
        # Ensure minimum safe calories (1200 for women, 1500 for men)
        min_calories = 1200 if self.gender == self.Gender.FEMALE else 1500
        calories = max(calories, min_calories)
        
        return round(calories, 2)

    def calculate_macros(self):
        """Calculate recommended daily macros (protein, carbs, fat in grams)"""
        calories = self.calculate_daily_calories()
        if not calories:
            return None
        
        # Macro ratios based on goal
        if self.nutritional_goal == self.NutritionalGoal.LOSE_WEIGHT:
            protein_ratio = 0.40  # 40% protein
            carb_ratio = 0.30     # 30% carbs
            fat_ratio = 0.30      # 30% fat
        elif self.nutritional_goal == self.NutritionalGoal.GAIN_WEIGHT:
            protein_ratio = 0.30  # 30% protein
            carb_ratio = 0.50     # 50% carbs
            fat_ratio = 0.20      # 20% fat
        else:  # MAINTAIN_WEIGHT
            protein_ratio = 0.30  # 30% protein
            carb_ratio = 0.40     # 40% carbs
            fat_ratio = 0.30      # 30% fat
        
        return {
            'protein': round((calories * protein_ratio) / 4, 1),      # 4 cal/g
            'carbohydrates': round((calories * carb_ratio) / 4, 1),   # 4 cal/g
            'fat': round((calories * fat_ratio) / 9, 1),              # 9 cal/g
        }

    def perform_calculations(self):
        """
        Perform all nutritional calculations and save to database
        Returns True if successful, False otherwise
        """
        from django.utils import timezone
        
        # Check if all required data is present
        required_fields = [
            self.weight, self.height, self.date_of_birth,
            self.gender, self.physical_activity, self.nutritional_goal
        ]
        
        if not all(required_fields):
            return False
        
        # Calculate all values
        self.bmi = self.calculate_bmi()
        
        if self.calculation_method == self.CalculationMethod.HARRIS_BENEDICT:
            self.ppm = self.calculate_ppm_harris_benedict()
        else:
            self.ppm = self.calculate_ppm_mifflin()
        
        self.cpm = self.calculate_cpm()
        self.daily_calories = self.calculate_daily_calories()
        
        macros = self.calculate_macros()
        if macros:
            self.daily_protein = macros['protein']
            self.daily_carbohydrates = macros['carbohydrates']
            self.daily_fat = macros['fat']
        
        self.calculations_last_updated = timezone.now()
        
        # Save to database
        self.save(update_fields=[
            'bmi', 'ppm', 'cpm', 'daily_calories',
            'daily_protein', 'daily_carbohydrates', 'daily_fat',
            'calculations_last_updated'
        ])
        
        return True

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        