from django.db import models

from profiles.models import Profile
from recipes.models import Recipe


# For History of recommendations
class Recommendation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recommendations')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    recommended_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "Recommendations"

# For user rating
class Rating(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    rating = models.IntegerField(null=True, blank=True)  # 1-5 gwiazdek
    interacted_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Ratings"
        unique_together = ('profile', 'recipe')