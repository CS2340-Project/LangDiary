from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Goal, Profile


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
        # Use reverse to get the actual URLs
        self.register_url = reverse('users.register')
        self.login_url = reverse('users.login')
        self.logout_url = reverse('users.logout')

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
        self.assertEqual(response.status_code, 405)


class UserAuthViewsTest(TestCase):
    """Tests for authentication-related views."""

    def setUp(self):
        self.client = Client()
        # Use reverse to get the actual URLs
        self.register_url = reverse('users.register')
        self.login_url = reverse('users.login')
        self.profile_url = reverse('users.profile')

        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )

        # Create profile if not automatically created by signal
        try:
            _ = self.user.profile
        except:
            Profile.objects.create(user=self.user)

    def test_register_view_get(self):
        """Test register view returns correct template."""
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_login_view_get(self):
        """Test login view returns correct template."""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_profile_view_authenticated(self):
        """Test that profile view is accessible to authenticated users."""
        # Login user first
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
        self.register_url = reverse('users.register')

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


class GoalFunctionalityTest(TestCase):
    """Tests for goal-related functionality."""

    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='goaluser',
            email='goal@example.com',
            password='securepassword123'
        )

        # Create profile if not automatically created by signal
        try:
            _ = self.user.profile
        except:
            Profile.objects.create(user=self.user)

        # Ensure the user is logged in
        self.client.login(username='goaluser', password='securepassword123')

        # URLs
        self.profile_url = reverse('users.profile')
        self.create_goal_url = reverse('users.create_goal')

        # Test goal data
        self.goal_data = {
            'goal_title': 'Learn French',
            'goal_description': 'Reach B1 level',
            'goal_target': 100,
            'goal_unit': 'hours',
            'goal_deadline': '2023-12-31'
        }

    def test_create_goal(self):
        """Test creating a new goal."""
        response = self.client.post(self.create_goal_url, self.goal_data)

        # Should redirect to profile
        self.assertEqual(response.status_code, 302)

        # Check if goal was created
        self.assertTrue(Goal.objects.filter(user=self.user, title='Learn French').exists())

    def test_edit_goal(self):
        """Test editing an existing goal."""
        # Create a goal first
        goal = Goal.objects.create(
            user=self.user,
            title='Original Title',
            description='Original Description',
            target_value=50,
            current_value=10,
            unit='pages',
            deadline='2023-10-15'
        )

        # Edit data
        edit_data = {
            'goal_title': 'Updated Title',
            'goal_description': 'Updated Description',
            'goal_target': 75,
            'goal_current': 20,
            'goal_unit': 'chapters',
            'goal_deadline': '2023-11-15'
        }

        edit_url = reverse('users.edit_goal', kwargs={'goal_id': goal.id})
        response = self.client.post(edit_url, edit_data)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Refresh from database
        goal.refresh_from_db()

        # Check if goal was updated
        self.assertEqual(goal.title, 'Updated Title')
        self.assertEqual(goal.target_value, 75)
        self.assertEqual(goal.current_value, 20)

    def test_delete_goal(self):
        """Test deleting a goal."""
        # Create a goal first
        goal = Goal.objects.create(
            user=self.user,
            title='Goal to Delete',
            target_value=100,
            current_value=0,
            unit='words'
        )

        delete_url = reverse('users.delete_goal', kwargs={'goal_id': goal.id})
        response = self.client.post(delete_url)

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Check if goal was deleted
        self.assertFalse(Goal.objects.filter(id=goal.id).exists())

    def test_update_goal_progress(self):
        """Test updating the progress of a goal."""
        # Create a goal first
        goal = Goal.objects.create(
            user=self.user,
            title='Progress Goal',
            target_value=100,
            current_value=30,
            unit='pages'
        )

        update_url = reverse('users.update_goal_progress', kwargs={'goal_id': goal.id})
        response = self.client.post(update_url, {'current_value': 50})

        # Check redirect
        self.assertEqual(response.status_code, 302)

        # Refresh from database
        goal.refresh_from_db()

        # Check if progress was updated
        self.assertEqual(goal.current_value, 50)