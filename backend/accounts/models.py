from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    We're using AbstractUser which already provides:
    - username: unique username for login
    - email: email address  
    - password: hashed password
    - first_name, last_name: optional name fields
    - is_active: whether the account is active
    - is_staff: whether user can access admin panel
    - is_superuser: whether user has all permissions
    - date_joined: timestamp when account was created
    - last_login: timestamp of last login
    
    Email verification is handled by django-allauth's EmailAddress model,
    so we don't need to add any extra fields for that.
    
    Why create a CustomUser at all if we don't add fields?
    - It's a Django best practice to use a custom user model from the start
    - Makes it easy to add fields later without complex migrations
    - Gives us full control over the user model
    """
    
    # Make email field required and unique
    email = models.EmailField(unique=True)
    
    # When creating superuser via command line, Django will ask for these fields
    # in addition to username and password
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
