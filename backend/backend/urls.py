"""
URL configuration for backend project.

Main URL router - includes all app URLs here.
All API endpoints will be under /api/v1/ prefix.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel
    # Access at: http://localhost:8000/admin/
    path('admin/', admin.site.urls),
    
    # API endpoints (version 1)
    # All authentication endpoints will be under /api/v1/auth/
    # Example: http://localhost:8000/api/v1/auth/login/
    path('api/v1/', include('accounts.urls')),
]
