from django.db import models
from django.conf import settings

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
        OTHER = 'O', 'Inna'

    class NutritionalGoal(models.TextChoices):
        LOSE_WEIGHT = 'LOSE', 'Lose Weight'
        MAINTAIN_WEIGHT = 'MAINTAIN', 'Maintain Weight'
        GAIN_WEIGHT = 'GAIN', 'Gain Weight'

    class PhysicalActivity(models.TextChoices):
        SEDENTARY = 'SEDENTARY', 'Sedentary (little or no exercise)'
        LIGHTLY_ACTIVE = 'LIGHT', 'Lightly active (light exercise/sports 1-3 days/week)'
        MODERATELY_ACTIVE = 'MODERATE', 'Moderately active (moderate exercise/sports 3-5 days/week)'
        VERY_ACTIVE = 'VERY', 'Very active (hard exercise/sports 6-7 days a week)'
        EXTRA_ACTIVE = 'EXTRA', 'Extra active (very hard exercise/sports & physical job)'

    gender = models.CharField(
        max_length=3,
        choices=Gender.choices,
        null=True,
        blank=True
    )
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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    