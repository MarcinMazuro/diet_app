from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from allauth.account.models import EmailAddress

User = get_user_model()


@override_settings(
    ACCOUNT_EMAIL_VERIFICATION='none',  # Disable email verification completely for tests
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'  # Use in-memory email backend
)
class UserRegistrationTestCase(APITestCase):
    """
    Test suite for user registration endpoint.
    
    Tests cover:
    - Successful registration
    - Invalid data handling
    - Duplicate username/email handling
    - Password validation
    """
    
    def setUp(self):
        """
        Set up test data that will be used across multiple tests.
        
        setUp() runs before each test method.
        This ensures each test starts with a clean state.
        """
        self.register_url = '/api/v1/auth/registration/'
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123',
            'password2': 'SecurePass123'
        }
    
    def test_user_registration_success(self):
        """
        Test that a user can successfully register with valid data.
        
        Expected behavior:
        - HTTP 201 Created status
        - User created in database
        - JWT tokens returned (access & refresh)
        - User data returned in response
        """
        response = self.client.post(self.register_url, self.valid_payload)
        
        # Check response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check JWT tokens are returned
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Check user data is returned
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        
        # Verify user was created in database
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_registration_with_mismatched_passwords(self):
        """
        Test that registration fails when passwords don't match.
        """
        payload = self.valid_payload.copy()
        payload['password2'] = 'DifferentPassword123'
        
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_registration_with_duplicate_username(self):
        """
        Test that registration fails when username already exists.
        """
        # Create first user
        User.objects.create_user(
            username='testuser',
            email='first@example.com',
            password='Password123'
        )
        
        # Try to register with same username
        response = self.client.post(self.register_url, self.valid_payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # Still only one user
    
    def test_registration_with_duplicate_email(self):
        """
        Test that registration fails when email already exists.
        """
        # Create user with the test email
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='ExistingPass123'
        )
        
        # Try to register with duplicate email but different username
        payload = {
            'username': 'newuser',
            'email': 'test@example.com',  # Duplicate!
            'password1': 'SecurePass456',
            'password2': 'SecurePass456'
        }
        
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should still be only 1 user (existinguser)
        self.assertEqual(User.objects.count(), 1)
    
    def test_registration_with_invalid_email(self):
        """
        Test that registration fails with invalid email format.
        """
        payload = self.valid_payload.copy()
        payload['email'] = 'not-an-email'
        
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_registration_with_short_password(self):
        """
        Test that registration fails with password shorter than 8 characters.
        """
        payload = self.valid_payload.copy()
        payload['password1'] = 'Short1'
        payload['password2'] = 'Short1'
        
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_registration_with_missing_fields(self):
        """
        Test that registration fails when required fields are missing.
        """
        # Missing email
        payload = {'username': 'test', 'password1': 'Pass123', 'password2': 'Pass123'}
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing username
        payload = {'email': 'test@example.com', 'password1': 'Pass123', 'password2': 'Pass123'}
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing passwords
        payload = {'username': 'test', 'email': 'test@example.com'}
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """
    Test suite for user login endpoint.
    
    Tests cover:
    - Login with username
    - Login with email
    - Invalid credentials handling
    - JWT token generation
    """
    
    def setUp(self):
        """
        Create a test user for login tests.
        """
        self.login_url = '/api/v1/auth/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123'
        )
        
        # Create and verify EmailAddress for django-allauth
        # This is required because ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True  # Mark as verified so user can login
        )
    
    def test_login_with_username(self):
        """
        Test that user can login with username and password.
        """
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123'
        }
        
        response = self.client.post(self.login_url, payload)
        
        # Debug: print response if test fails
        if response.status_code != status.HTTP_200_OK:
            print(f"\nLogin with username failed. Response: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_with_email(self):
        """
        Test that user can login with email and password.
        Note: dj-rest-auth requires 'username' field even when using email to login.
        """
        # Verify EmailAddress exists and is verified
        email_obj = EmailAddress.objects.filter(user=self.user, verified=True).first()
        if not email_obj:
            print(f"\nWARNING: No verified EmailAddress found for user {self.user.username}")
        else:
            print(f"\nEmailAddress found: {email_obj.email}, verified={email_obj.verified}")
        
        payload = {
            'username': 'test@example.com',  # Use 'username' field with email value
            'password': 'SecurePass123'
        }
        
        response = self.client.post(self.login_url, payload)
        
        # Debug: print response if test fails
        if response.status_code != status.HTTP_200_OK:
            print(f"\nLogin with email failed. Response: {response.data}")
            print(f"User exists: {User.objects.filter(email='test@example.com').exists()}")
            print(f"User can authenticate: {self.user.check_password('SecurePass123')}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_with_wrong_password(self):
        """
        Test that login fails with incorrect password.
        """
        payload = {
            'username': 'testuser',
            'password': 'WrongPassword123'
        }
        
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)
    
    def test_login_with_nonexistent_user(self):
        """
        Test that login fails for non-existent user.
        """
        payload = {
            'username': 'nonexistent',
            'password': 'Password123'
        }
        
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_missing_credentials(self):
        """
        Test that login fails when credentials are missing.
        """
        # Missing password
        response = self.client.post(self.login_url, {'username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing username/email
        response = self.client.post(self.login_url, {'password': 'Pass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTTokenTestCase(APITestCase):
    """
    Test suite for JWT token operations.
    
    Tests cover:
    - Token refresh
    - Token expiration
    - Using tokens for authentication
    """
    
    def setUp(self):
        """
        Create user and get JWT tokens.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123'
        )
        
        # Verify email for django-allauth
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True
        )
        
        # Login to get tokens
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'SecurePass123'
        })
        
        self.access_token = login_response.data['access']
        self.refresh_token = login_response.data['refresh']
    
    def test_access_protected_endpoint_with_token(self):
        """
        Test that authenticated user can access protected endpoints.
        """
        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Access protected endpoint
        response = self.client.get('/api/v1/auth/user/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_access_protected_endpoint_without_token(self):
        """
        Test that unauthenticated requests are rejected.
        """
        response = self.client.get('/api/v1/auth/user/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """
        Test that refresh token can be used to get new access token.
        """
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': self.refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        # With ROTATE_REFRESH_TOKENS=True, we also get new refresh token
        self.assertIn('refresh', response.data)
    
    def test_refresh_with_invalid_token(self):
        """
        Test that refresh fails with invalid token.
        """
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': 'invalid.token.here'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLogoutTestCase(APITestCase):
    """
    Test suite for user logout endpoint.
    
    Tests token blacklisting on logout.
    """
    
    def setUp(self):
        """
        Create user and login.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123'
        )
        
        # Verify email for django-allauth
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            primary=True,
            verified=True
        )
        
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'SecurePass123'
        })
        
        self.access_token = login_response.data['access']
        self.refresh_token = login_response.data['refresh']
    
    def test_logout_success(self):
        """
        Test that user can successfully logout.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post('/api/v1/auth/logout/', {
            'refresh': self.refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cannot_use_token_after_logout(self):
        """
        Test that refresh token cannot be used after logout (blacklisted).
        """
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.client.post('/api/v1/auth/logout/', {
            'refresh': self.refresh_token
        })
        
        # Try to use blacklisted refresh token
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': self.refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
