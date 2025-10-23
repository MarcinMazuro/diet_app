from django.urls import path, include
from .views import string_response, test_user, random_data, meal

app_name = 'test_endpoints'
urlpatterns = [
    path('string/', string_response, name='string_response'),
    path('user/', test_user, name='test_user'),
    path('random/', random_data, name='random_data'),
    path('meal/', meal, name='meal'),
]