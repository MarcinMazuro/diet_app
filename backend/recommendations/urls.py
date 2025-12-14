from django.urls import path
from . import views

urlpatterns = [
    # Recommendations
    path('recipes/recommended/', views.recommend_recipe, name='recommend_recipes'),  # POST - get recommendation
    path('daily-plans/', views.generate_daily_meal_plan, name='generate_daily_plan'),  # POST - generate daily plan

    # Meal Plans - RESTful CRUD
    path('meal-plans/', views.meal_plans_list, name='meal_plans_list'),  # GET - list, POST - create
    path('meal-plans/<int:plan_id>/', views.meal_plan_detail, name='meal_plan_detail'),  # GET, PATCH, DELETE

    # Ratings - RESTful CRUD
    path('ratings/', views.ratings_list, name='ratings_list'),  # GET - list all, POST - create
    path('ratings/<int:recipe_id>/', views.rating_detail, name='rating_detail'),  # GET, PATCH, DELETE
]

