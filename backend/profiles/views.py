from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Profile
from .serializers import ProfileSerializer

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the profile of the currently authenticated user."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
