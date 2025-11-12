from django.urls import path
from . import views

urlpatterns = [
    path('random/', views.random_recipe, name='random-recipe'),
    path('', views.list_recipes, name='list-recipes'),
    path('<int:recipe_id>/', views.get_recipe, name='get-recipe'),
]

