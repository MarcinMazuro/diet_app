from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_recipe, name='recommend_recipes'),
    path('daily-plan/', views.generate_daily_plan, name='generate_daily_plan'),
    path('rate/', views.rate_recipe, name='rate_recipe'),
    path('my-recommendations/', views.recommendations_history, name='recommendations_history'),
    path('my-ratings/', views.ratings_history, name='ratings_history')
]

