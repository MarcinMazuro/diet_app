from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer

# Get our CustomUser model
User = get_user_model()


class RegisterSerializer(BaseRegisterSerializer):
    """
    Custom registration serializer.
    
    Inherits from dj-rest-auth's RegisterSerializer which provides:
    - username field with validation
    - email field with validation
    - password1 and password2 fields (password confirmation)
    - Basic validation (passwords match, username unique, etc.)
    
    We're keeping it simple - just username, email, and password required.
    All other fields (first_name, last_name, etc.) can be added later via profile update.
    
    How it works:
    1. User sends: {username, email, password1, password2}
    2. Serializer validates data
    3. If valid, save() method creates the user
    4. django-allauth automatically sends verification email
    """
    
    def validate_email(self, email):
        """
        Check that email is unique before allowing registration.
        """
        email = email.lower()  # Normalize email to lowercase
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return email
    
    def save(self, request):
        """
        Create and return a new user instance.
        
        The parent class (BaseRegisterSerializer) handles:
        - Password validation
        - Username uniqueness check
        - Email format validation
        - Creating the user in database
        - Sending verification email (via django-allauth)
        
        We just call super().save() to use all that functionality.
        """
        user = super().save(request)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    
    Used when:
    - GET /api/auth/user/ - get current user info
    - Response after login/registration
    
    Shows basic user info. Does NOT include sensitive data like:
    - password (never return this!)
    - is_staff, is_superuser (internal flags)
    
    ModelSerializer automatically:
    - Creates fields based on the model
    - Handles validation
    - Provides default create() and update() methods
    """
    
    class Meta:
        model = User
        
        # Fields to include in JSON response
        fields = [
            'id',           # User's unique ID
            'username',     # Username
            'email',        # Email address
            'first_name',   # Optional first name
            'last_name',    # Optional last name
        ]
        
        # Fields that cannot be modified via API
        # (id and email should not change after creation)
        read_only_fields = ['id', 'email']
