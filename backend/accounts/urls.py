from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView


app_name = 'accounts'
urlpatterns = [
    # dj-rest-auth provides these endpoints:
    # POST /login/ - Login with username/email and password, returns JWT tokens
    # POST /logout/ - Logout (blacklists refresh token)
    # GET /user/ - Get current user details
    # POST /password/reset/ - Request password reset email
    # POST /password/reset/confirm/ - Confirm password reset with token
    path('auth/', include('dj_rest_auth.urls')),
    
    # dj-rest-auth registration provides these endpoints:
    # POST /registration/ - Register new user (username, email, password1, password2)
    # POST /registration/verify-email/ - Verify email with key from email
    # POST /registration/resend-email/ - Resend verification email
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # django-allauth account URLs (required for email verification)
    # This provides the 'account_confirm_email' URL that allauth needs
    path('auth/account/', include('allauth.account.urls')),
    
    # JWT token refresh endpoint
    # POST /auth/token/refresh/ - Refresh access token using refresh token
    # Request: {"refresh": "your_refresh_token"}
    # Response: {"access": "new_access_token", "refresh": "new_refresh_token"}
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]