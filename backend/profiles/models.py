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
        """
        Calculate recommended daily macros (protein, carbs, fat in grams)
        Protein is calculated per kg of body weight based on activity level
        Carbs and fats are calculated as percentages of remaining calories
        """
        calories = self.calculate_daily_calories()
        if not calories or not self.weight:
            return None
        
        weight_kg = float(self.weight)
        
        # PROTEIN: Calculate based on activity level (g/kg body weight)
        if self.nutritional_goal == self.NutritionalGoal.LOSE_WEIGHT:
            # Higher protein during weight loss to preserve muscle
            protein_per_kg = {
                self.PhysicalActivity.SEDENTARY: 1.6,      # 1.6 g/kg
                self.PhysicalActivity.LOW: 1.8,            # 1.8 g/kg
                self.PhysicalActivity.MODERATE: 2.0,       # 2.0 g/kg
                self.PhysicalActivity.HIGH: 2.2,           # 2.2 g/kg
                self.PhysicalActivity.VERY_HIGH: 2.4,      # 2.4 g/kg
            }
        elif self.nutritional_goal == self.NutritionalGoal.GAIN_WEIGHT:
            # Moderate to high protein for muscle building
            protein_per_kg = {
                self.PhysicalActivity.SEDENTARY: 1.4,      # 1.4 g/kg
                self.PhysicalActivity.LOW: 1.6,            # 1.6 g/kg
                self.PhysicalActivity.MODERATE: 1.8,       # 1.8 g/kg
                self.PhysicalActivity.HIGH: 2.0,           # 2.0 g/kg
                self.PhysicalActivity.VERY_HIGH: 2.2,      # 2.2 g/kg
            }
        else:  # MAINTAIN_WEIGHT
            # Standard protein intake
            protein_per_kg = {
                self.PhysicalActivity.SEDENTARY: 1.2,      # 1.2 g/kg
                self.PhysicalActivity.LOW: 1.4,            # 1.4 g/kg
                self.PhysicalActivity.MODERATE: 1.6,       # 1.6 g/kg
                self.PhysicalActivity.HIGH: 1.8,           # 1.8 g/kg
                self.PhysicalActivity.VERY_HIGH: 2.0,      # 2.0 g/kg
            }
        
        protein_grams = weight_kg * protein_per_kg.get(self.physical_activity, 1.6)
        protein_calories = protein_grams * 4  # 4 kcal per gram of protein
        
        # Remaining calories after protein
        remaining_calories = calories - protein_calories
        
        # FAT and CARBS: Calculate percentages based on goal and activity
        if self.nutritional_goal == self.NutritionalGoal.LOSE_WEIGHT:
            # Lower carbs, moderate fat for weight loss
            if self.physical_activity in [self.PhysicalActivity.HIGH, self.PhysicalActivity.VERY_HIGH]:
                # More active = need more carbs for energy
                fat_percentage = 0.25      # 25% fat
                carb_percentage = 0.75     # 75% carbs
            else:
                fat_percentage = 0.35      # 35% fat
                carb_percentage = 0.65     # 65% carbs
                
        elif self.nutritional_goal == self.NutritionalGoal.GAIN_WEIGHT:
            # Higher carbs for muscle building and energy
            if self.physical_activity in [self.PhysicalActivity.HIGH, self.PhysicalActivity.VERY_HIGH]:
                fat_percentage = 0.20      # 20% fat
                carb_percentage = 0.80     # 80% carbs
            else:
                fat_percentage = 0.25      # 25% fat
                carb_percentage = 0.75     # 75% carbs
                
        else:  # MAINTAIN_WEIGHT
            # Balanced distribution
            if self.physical_activity in [self.PhysicalActivity.HIGH, self.PhysicalActivity.VERY_HIGH]:
                fat_percentage = 0.25      # 25% fat
                carb_percentage = 0.75     # 75% carbs
            else:
                fat_percentage = 0.30      # 30% fat
                carb_percentage = 0.70     # 70% carbs
        
        fat_calories = remaining_calories * fat_percentage
        carb_calories = remaining_calories * carb_percentage
        
        fat_grams = fat_calories / 9      # 9 kcal per gram of fat
        carb_grams = carb_calories / 4    # 4 kcal per gram of carbs
        
        return {
            'protein': round(protein_grams, 1),
            'carbohydrates': round(carb_grams, 1),
            'fat': round(fat_grams, 1),
            'protein_per_kg': round(protein_grams / weight_kg, 2),
            'calories_from_protein': round(protein_calories, 0),
            'calories_from_carbs': round(carb_calories, 0),
            'calories_from_fat': round(fat_calories, 0),
            'protein_percentage': round((protein_calories / calories) * 100, 1),
            'carb_percentage': round((carb_calories / calories) * 100, 1),
            'fat_percentage': round((fat_calories / calories) * 100, 1)
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
        