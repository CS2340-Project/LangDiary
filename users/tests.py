from django.test import TestCase, Client
from django.contrib.auth.models import User

class UserModelTest(TestCase):
    """Tests for the User model functionality."""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test that a user can be created."""
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('securepassword123'))

    def test_user_str_method(self):
        """Test the string representation of a user."""
        self.assertEqual(str(self.user), 'testuser')


class UserAuthenticationTest(TestCase):
    """Tests for user authentication functionality."""

    def setUp(self):
        self.client = Client()
        self.register_url = 'users.register'
        self.login_url = 'users.login'
        self.logout_url = 'users.logout'
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        }

    def test_user_registration(self):
        """Test user registration process."""
        response = self.client.post(self.register_url, self.user_data)

        # Check for redirect after successful registration
        self.assertEqual(response.status_code, 302)

        # Check if user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        """Test user login process."""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )

        # Attempt login
        login_data = {
            'username': 'testuser',
            'password': 'securepassword123'
        }
        response = self.client.post(self.login_url, login_data)

        # Check for redirect after successful login
        self.assertEqual(response.status_code, 302)

        # Check if user is authenticated
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)

    def test_user_logout(self):
        """Test user logout process."""
        # Create and login user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )

        self.client.login(username='testuser', password='securepassword123')

        # Logout
        response = self.client.get(self.logout_url)

        # Check for redirect after logout
        self.assertEqual(response.status_code, 302)


class UserAuthViewsTest(TestCase):
    """Tests for authentication-related views."""

    def setUp(self):
        self.client = Client()
        self.register_url = 'users.register'
        self.login_url = 'users.login'
        self.profile_url = 'users.profile'  # Assuming you have a profile page

        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )

    def test_register_view_get(self):
        """Test register view returns correct template."""
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')  # Adjust template name if needed

    def test_login_view_get(self):
        """Test login view returns correct template."""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')  # Adjust template name if needed

    def test_profile_view_authenticated(self):
        """Test that profile view is accessible to authenticated users."""
        self.client.login(username='testuser', password='securepassword123')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)

    def test_profile_view_unauthenticated(self):
        """Test that profile view redirects unauthenticated users."""
        response = self.client.get(self.profile_url)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class UserFormValidationTest(TestCase):
    """Tests for user-related form validation."""

    def setUp(self):
        self.client = Client()
        self.register_url = 'users.register'

        # Create a user to test duplicate validation
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='securepassword123'
        )

    def test_registration_password_mismatch(self):
        """Test validation for password mismatch during registration."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'password123',
            'password2': 'different_password'
        }

        response = self.client.post(self.register_url, data)

        # Form should not submit successfully
        self.assertEqual(response.status_code, 200)

        # No new user should be created
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_registration_duplicate_username(self):
        """Test validation for duplicate username during registration."""
        data = {
            'username': 'existinguser',  # Already exists
            'email': 'new@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        }

        response = self.client.post(self.register_url, data)

        # Form should not submit successfully
        self.assertEqual(response.status_code, 200)

        # Only one user with this username should exist
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_registration_weak_password(self):
        """Test validation for weak password during registration."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'password',  # Too common/simple
            'password2': 'password'
        }

        response = self.client.post(self.register_url, data)

        # Form should not submit successfully
        self.assertEqual(response.status_code, 200)

        # No new user should be created
        self.assertFalse(User.objects.filter(username='newuser').exists())