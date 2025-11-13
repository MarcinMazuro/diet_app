from django.urls import path
from .views import (
    ProfileDetailView, 
    calculate_and_save_nutrition,
    get_saved_calculations
)

urlpatterns = [
    path('me/', ProfileDetailView.as_view(), name='profile-me'),
    path('calculate/', calculate_and_save_nutrition, name='calculate-nutrition'),
    path('calculations/', get_saved_calculations, name='get-calculations')
]
