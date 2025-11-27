from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class NutritionalGoal(models.TextChoices):
        LOSE_WEIGHT = 'LOSE', 'Lose Weight'
        MAINTAIN_WEIGHT = 'MAINTAIN', 'Maintain Weight'
        GAIN_WEIGHT = 'GAIN', 'Gain Weight'

    class PhysicalActivity(models.TextChoices):
        SEDENTARY = 'SEDENTARY', 'Sedentary (PAL: 1.2)'
        LOW = 'LOW', 'Low activity (PAL: 1.4-1.5)'
        MODERATE = 'MODERATE', 'Moderate activity (PAL: 1.6-1.7)'
        HIGH = 'HIGH', 'High activity (PAL: 1.8-2.0)'
        VERY_HIGH = 'VERY_HIGH', 'Very high activity (PAL: 2.1-2.4)'

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
    gender = models.CharField(max_length=3, choices=Gender.choices, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(500)]
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(300)]
    )
    
    # Goals and preferences
    nutritional_goal = models.CharField(max_length=10, choices=NutritionalGoal.choices, null=True, blank=True)
    physical_activity = models.CharField(max_length=10, choices=PhysicalActivity.choices, null=True, blank=True)
    
    # Calculation parameters (set during calculation)
    calculation_method = models.CharField(max_length=20, choices=CalculationMethod.choices, null=True, blank=True)
    calorie_adjustment = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(-1000), MaxValueValidator(1000)]
    )
    custom_protein_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    custom_carb_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    custom_fat_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Calculated values (stored for quick access)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ppm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    cpm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    daily_calories = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    daily_protein = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    daily_carbohydrates = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    daily_fat = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    protein_per_kg = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    protein_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    carb_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    
    # Timestamps
    calculations_last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        