from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Get our CustomUser model
User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for CustomUser model.
    
    Inherits from Django's UserAdmin which provides:
    - User list view with filters and search
    - User detail/edit view with organized fieldsets
    - Password change functionality
    - Permissions management
    
    We customize it to show our email field prominently and add email verification status.
    """
    
    # Fields to display in the user list view (admin home page)
    # These columns will be shown in the table
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    ]
    
    # Add filters in the right sidebar
    # Makes it easy to filter users by status
    list_filter = [
        'is_staff',
        'is_active',
        'is_superuser',
        'date_joined',
    ]
    
    # Fields that are searchable from the search bar
    # User can search by any of these fields
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]
    
    # Default ordering in list view (newest users first)
    ordering = ['-date_joined']
    
    # Organize fields into sections in the user detail page
    # This is what you see when clicking on a user
    fieldsets = (
        # Section 1: Login credentials
        (None, {
            'fields': ('username', 'password')
        }),
        
        # Section 2: Personal information
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        
        # Section 3: Permissions
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        
        # Section 4: Important dates (read-only)
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    # Fields layout when adding a new user through admin
    # Simpler than the full fieldsets above
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # Makes the form wider
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_active',
            ),
        }),
    )
    
    # Fields that cannot be edited (only viewed)
    readonly_fields = ['date_joined', 'last_login']
