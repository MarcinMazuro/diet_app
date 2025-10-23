from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random


@api_view(['GET'])
def string_response(request):
    return Response({'message': 'This is a string response'})


@api_view(['GET'])
def test_user(request):
    data = {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com'
    }
    return Response(data)


@api_view(['POST'])
def random_data(request):
    options = request.data.get('options', [])
    
    if not options:
        return Response(
            {'error': 'No options provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    choice = random.choice(options)
    return Response({'selected': choice})


@api_view(['GET'])
def meal(request):
    data = {
        'meal': 'tatra 500 ml',
        'calories': 205,
        'fat': 0,
        'carbohydrates': 14,
        'protein': 0,
        'fiber': 0,
        'ingredients': ['water', 'malted barley', 'hops', 'yeast']
    }
    return Response(data)