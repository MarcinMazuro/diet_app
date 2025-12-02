from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_recipe, name='recommend_recipes'),
    path('daily-plan/', views.generate_daily_plan, name='generate_daily_plan'),

    # Ratings CRUD
    path('ratings/', views.rate_recipe, name='create_rating'),  # POST - create rating (body: recipe_id, rating)
    path('ratings/<int:recipe_id>/', views.rate_recipe, name='update_rating'),  # PUT - update rating
    path('ratings/<int:recipe_id>/get/', views.get_rating, name='get_rating'),  # GET - get single rating
    path('ratings/<int:recipe_id>/delete/', views.delete_rating, name='delete_rating'),  # DELETE - delete rating
    path('my-ratings/', views.ratings_history, name='ratings_history'),  # GET - get all user ratings

    # History
    path('my-recommendations/', views.recommendations_history, name='recommendations_history'),
]

