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
        null=True, 
        blank=True,
        default=None,
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
    protein_per_kg = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    help_text="Protein intake per kg of body weight"
    )
    protein_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Percentage of calories from protein"
    )
    carb_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Percentage of calories from carbohydrates"
    )
    fat_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Percentage of calories from fat"
    )
    custom_protein_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(0.7)],
        help_text="Custom protein percentage (0.0 to 1.0). Leave empty for automatic calculation."
    )
    custom_carb_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(0.8)],
        help_text="Custom carbohydrate percentage (0.0 to 1.0). Leave empty for automatic calculation."
    )
    custom_fat_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(0.7)],
        help_text="Custom fat percentage (0.0 to 1.0). Leave empty for automatic calculation."
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

    def get_recommended_calculation_method(self):
        """
        Auto-select calculation method based on user characteristics
        Based on the image criteria:
        - Harris-Benedict: for normal BMI, not overweight, people who exercise regularly
        - Mifflin: for overweight people
        """
        bmi = self.calculate_bmi()
        if not bmi:
            return self.CalculationMethod.MIFFLIN  # default
        
        # BMI categories:
        # Underweight: < 18.5
        # Normal: 18.5 - 24.9
        # Overweight: 25 - 29.9
        # Obese: >= 30
        
        if bmi >= 25:  # Overweight or obese
            return self.CalculationMethod.MIFFLIN
        else:  # Normal or underweight
            return self.CalculationMethod.HARRIS_BENEDICT

    def calculate_daily_calories(self):
        """
        Calculate recommended daily calories based on nutritional goal
        Uses user's calorie_adjustment if explicitly set, otherwise uses defaults
        - None: uses default adjustment based on goal
        - 0: explicitly no adjustment (maintains CPM)
        - Other value: uses that specific adjustment
        """
        cpm = self.calculate_cpm()
        if not cpm or not self.nutritional_goal:
            return None
        
        # Default calorie adjustments based on goal
        default_adjustments = {
            self.NutritionalGoal.LOSE_WEIGHT: -500,
            self.NutritionalGoal.GAIN_WEIGHT: 500,
            self.NutritionalGoal.MAINTAIN_WEIGHT: 0
        }
        
        # Determine which adjustment to use
        if self.calorie_adjustment is None:
            # Not set - use default based on goal
            adjustment = default_adjustments.get(self.nutritional_goal, 0)
        else:
            # Explicitly set (including 0) - use that value
            adjustment = self.calorie_adjustment
        
        calories = cpm + adjustment
        
        # Ensure minimum safe calories (1200 for women, 1500 for men)
        if self.gender == self.Gender.FEMALE:
            min_calories = 1200
        elif self.gender == self.Gender.MALE:
            min_calories = 1400
        else:
            min_calories = 1300  # average
        
        calories = max(calories, min_calories)
        
        return round(calories, 2)

    def calculate_macros(self):
        """
        Calculate recommended daily macros (protein, carbs, fat in grams)
        Uses custom percentages if provided, otherwise calculates based on activity level
        """
        calories = self.calculate_daily_calories()
        if not calories or not self.weight:
            return None
        
        weight_kg = float(self.weight)
        
        # Check if user has specified custom macro percentages
        has_custom_macros = all([
            self.custom_protein_percentage is not None,
            self.custom_carb_percentage is not None,
            self.custom_fat_percentage is not None
        ])
        
        if has_custom_macros:
            # Use custom percentages
            protein_percentage = float(self.custom_protein_percentage)
            carb_percentage = float(self.custom_carb_percentage)
            fat_percentage = float(self.custom_fat_percentage)
            
            # Validate that they sum to 1.0 (with small tolerance for floating point errors)
            total = protein_percentage + carb_percentage + fat_percentage
            if abs(total - 1.0) > 0.01:  # Allow 1% tolerance
                # If they don't sum to 1, normalize them
                protein_percentage = protein_percentage / total
                carb_percentage = carb_percentage / total
                fat_percentage = fat_percentage / total
            
            # Calculate grams from percentages
            protein_calories = calories * protein_percentage
            carb_calories = calories * carb_percentage
            fat_calories = calories * fat_percentage
            
            protein_grams = protein_calories / 4
            carb_grams = carb_calories / 4
            fat_grams = fat_calories / 9
            
        else:
            # AUTOMATIC CALCULATION based on activity level
            
            # PROTEIN: Calculate based on activity level (g/kg body weight)
            if self.nutritional_goal == self.NutritionalGoal.LOSE_WEIGHT:
                protein_per_kg = {
                    self.PhysicalActivity.SEDENTARY: 1.6,
                    self.PhysicalActivity.LOW: 1.8,
                    self.PhysicalActivity.MODERATE: 2.0,
                    self.PhysicalActivity.HIGH: 2.2,
                    self.PhysicalActivity.VERY_HIGH: 2.4,
                }
            elif self.nutritional_goal == self.NutritionalGoal.GAIN_WEIGHT:
                protein_per_kg = {
                    self.PhysicalActivity.SEDENTARY: 1.4,
                    self.PhysicalActivity.LOW: 1.6,
                    self.PhysicalActivity.MODERATE: 1.8,
                    self.PhysicalActivity.HIGH: 2.0,
                    self.PhysicalActivity.VERY_HIGH: 2.2,
                }
            else:  # MAINTAIN_WEIGHT
                protein_per_kg = {
                    self.PhysicalActivity.SEDENTARY: 1.2,
                    self.PhysicalActivity.LOW: 1.4,
                    self.PhysicalActivity.MODERATE: 1.6,
                    self.PhysicalActivity.HIGH: 1.8,
                    self.PhysicalActivity.VERY_HIGH: 2.0,
                }
            
            protein_grams = weight_kg * protein_per_kg.get(self.physical_activity, 1.6)
            protein_calories = protein_grams * 4
            
            # Remaining calories after protein
            remaining_calories = calories - protein_calories
            
            # FAT and CARBS: Calculate percentages based on goal and activity
            if self.nutritional_goal == self.NutritionalGoal.LOSE_WEIGHT:
                if self.physical_activity in [self.PhysicalActivity.HIGH, self.PhysicalActivity.VERY_HIGH]:
                    fat_pct = 0.25
                    carb_pct = 0.75
                else:
                    fat_pct = 0.35
                    carb_pct = 0.65
            elif self.nutritional_goal == self.NutritionalGoal.GAIN_WEIGHT:
                if self.physical_activity in [self.PhysicalActivity.HIGH, self.PhysicalActivity.VERY_HIGH]:
                    fat_pct = 0.20
                    carb_pct = 0.80
                else:
                    fat_pct = 0.25
                    carb_pct = 0.75
            else:  # MAINTAIN_WEIGHT
                if self.physical_activity in [self.PhysicalActivity.HIGH, self.PhysicalActivity.VERY_HIGH]:
                    fat_pct = 0.25
                    carb_pct = 0.75
                else:
                    fat_pct = 0.30
                    carb_pct = 0.70
            
            fat_calories = remaining_calories * fat_pct
            carb_calories = remaining_calories * carb_pct
            
            fat_grams = fat_calories / 9
            carb_grams = carb_calories / 4
            
            # Calculate actual percentages for display
            protein_percentage = protein_calories / calories
            carb_percentage = carb_calories / calories
            fat_percentage = fat_calories / calories
        
        return {
            'protein': round(protein_grams, 1),
            'carbohydrates': round(carb_grams, 1),
            'fat': round(fat_grams, 1),
            'protein_per_kg': round(protein_grams / weight_kg, 2),
            'calories_from_protein': round(protein_calories, 0),
            'calories_from_carbs': round(carb_calories, 0),
            'calories_from_fat': round(fat_calories, 0),
            'protein_percentage': round(protein_percentage * 100, 1),
            'carb_percentage': round(carb_percentage * 100, 1),
            'fat_percentage': round(fat_percentage * 100, 1),
            'using_custom_percentages': has_custom_macros
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
        
        # Calculate BMI first
        self.bmi = self.calculate_bmi()
        
        # Auto-select calculation method if not explicitly set or if set to default
        if not self.calculation_method:
            self.calculation_method = self.get_recommended_calculation_method()
        
        # Calculate PPM based on method
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
            self.protein_per_kg = macros['protein_per_kg']
            self.protein_percentage = macros['protein_percentage']
            self.carb_percentage = macros['carb_percentage']
            self.fat_percentage = macros['fat_percentage']
        
        self.calculations_last_updated = timezone.now()
        
        # Save to database
        self.save(update_fields=[
            'bmi', 'calculation_method', 'ppm', 'cpm', 'daily_calories',
            'daily_protein', 'daily_carbohydrates', 'daily_fat',
            'protein_per_kg', 'protein_percentage', 'carb_percentage', 'fat_percentage',
            'calculations_last_updated'
        ])
        
        return True

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        