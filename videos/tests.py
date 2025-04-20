from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from unittest.mock import patch, MagicMock

from .models import LanguageVideo
from .forms import VideoGeneratorForm

class LanguageVideoModelTests(TestCase):
    """Tests for the LanguageVideo model."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a sample video
        self.video = LanguageVideo.objects.create(
            user=self.user,
            title='Test Spanish Grammar Video',
            youtube_id='abc123',
            language='spanish',
            level='beginner',
            video_type='lesson',
            duration='medium',
            description='A test video description',
            is_watched=False
        )
    
    def test_video_creation(self):
        """Test that a video can be created with the correct attributes."""
        self.assertEqual(self.video.title, 'Test Spanish Grammar Video')
        self.assertEqual(self.video.youtube_id, 'abc123')
        self.assertEqual(self.video.language, 'spanish')
        self.assertEqual(self.video.level, 'beginner')
        self.assertEqual(self.video.video_type, 'lesson')
        self.assertEqual(self.video.is_watched, False)
        self.assertEqual(self.video.user, self.user)
    
    def test_string_representation(self):
        """Test the string representation of a video."""
        self.assertEqual(str(self.video), 'Test Spanish Grammar Video')
    
    def test_mark_as_watched(self):
        """Test marking a video as watched."""
        self.assertFalse(self.video.is_watched)
        self.video.is_watched = True
        self.video.save()
        
        # Refresh from database
        self.video.refresh_from_db()
        self.assertTrue(self.video.is_watched)


class VideoGeneratorFormTests(TestCase):
    """Tests for the VideoGeneratorForm."""
    
    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            'language': 'spanish',
            'level': 'beginner',
            'video_type': 'lesson',
            'duration': 'medium',
            'count': '1'
        }
        form = VideoGeneratorForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_minimal_data(self):
        """Test form with only required fields."""
        form_data = {
            'language': 'french',
            'level': 'intermediate'
        }
        form = VideoGeneratorForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_data(self):
        """Test form with invalid data."""
        form_data = {
            'language': 'invalid',
            'level': 'beginner'
        }
        form = VideoGeneratorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('language', form.errors)


class VideoViewsTests(TestCase):
    """Tests for the video views."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a sample video
        self.video = LanguageVideo.objects.create(
            user=self.user,
            title='Test Spanish Grammar Video',
            youtube_id='abc123',
            language='spanish',
            level='beginner',
            video_type='lesson',
            duration='medium',
            description='A test video description',
            is_watched=False
        )
        
        # Set up client and login
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_index_view(self):
        """Test the index view."""
        response = self.client.get(reverse('videos:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/index.html')
        
        # Check context data
        self.assertEqual(response.context['current_video'], self.video)
        self.assertEqual(list(response.context['video_list']), [self.video])
        self.assertIsInstance(response.context['form'], VideoGeneratorForm)
    
    def test_index_view_with_video_id(self):
        """Test the index view with a specific video ID."""
        response = self.client.get(f"{reverse('videos:index')}?video_id={self.video.id}")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_video'], self.video)
    
    def test_mark_watched_view(self):
        """Test marking a video as watched."""
        self.assertFalse(self.video.is_watched)
        
        response = self.client.post(
            reverse('videos:mark_watched'),
            {'video_id': self.video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        
        # Refresh from database
        self.video.refresh_from_db()
        self.assertTrue(self.video.is_watched)
    
    def test_remove_video_view(self):
        """Test removing a video."""
        response = self.client.post(
            reverse('videos:remove_video'),
            {'video_id': self.video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        
        # Check that video is deleted
        self.assertEqual(LanguageVideo.objects.count(), 0)


class YouTubeApiIntegrationTests(TestCase):
    """Tests for YouTube API integration."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Set up client and login
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    @patch('videos.views.requests.get')
    def test_generate_videos_success(self, mock_get):
        """Test successful video generation."""
        # Mock search API response
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            'items': [
                {
                    'id': {'videoId': 'abc123'},
                    'snippet': {
                        'title': 'Test Video Title',
                        'description': 'Test description'
                    }
                }
            ]
        }
        
        # Mock video details API response
        mock_details_response = MagicMock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {
            'items': [
                {
                    'id': 'abc123',
                    'snippet': {
                        'title': 'Test Video Title',
                        'description': 'Test description'
                    },
                    'contentDetails': {
                        'duration': 'PT10M30S'  # 10 minutes, 30 seconds
                    }
                }
            ]
        }
        
        # Set up the mock to return different responses for different URLs
        def get_side_effect(url, *args, **kwargs):
            if 'search?' in url:
                return mock_search_response
            elif 'videos?' in url:
                return mock_details_response
            return None
        
        mock_get.side_effect = get_side_effect
        
        # Test the generate_videos view
        form_data = {
            'language': 'spanish',
            'level': 'beginner',
            'video_type': 'lesson',
            'duration': 'medium',
            'count': '1'
        }
        
        response = self.client.post(reverse('videos:generate'), form_data, follow=True)
        
        # Check that a video was created
        self.assertEqual(LanguageVideo.objects.count(), 1)
        video = LanguageVideo.objects.first()
        self.assertEqual(video.youtube_id, 'abc123')
        self.assertEqual(video.title, 'Test Video Title')
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully added a new video to your collection!")
    
    @patch('videos.views.requests.get')
    def test_generate_videos_no_results(self, mock_get):
        """Test video generation with no search results."""
        # Mock empty search API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        
        mock_get.return_value = mock_response
        
        # Test the generate_videos view
        form_data = {
            'language': 'spanish',
            'level': 'beginner'
        }
        
        response = self.client.post(reverse('videos:generate'), form_data, follow=True)
        
        # Check that no video was created
        self.assertEqual(LanguageVideo.objects.count(), 0)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No videos found matching your criteria. Try different search options.")
    
    @patch('videos.views.requests.get')
    def test_generate_videos_api_error(self, mock_get):
        """Test video generation with API error."""
        # Mock error API response
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            'error': {
                'message': 'API key not valid'
            }
        }
        
        mock_get.return_value = mock_response
        
        # Test the generate_videos view
        form_data = {
            'language': 'spanish',
            'level': 'beginner'
        }
        
        response = self.client.post(reverse('videos:generate'), form_data, follow=True)
        
        # Check that no video was created
        self.assertEqual(LanguageVideo.objects.count(), 0)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertTrue("Error contacting YouTube API" in str(messages[0]))


class DailyVideoTests(TestCase):
    """Tests for the daily video recommendation feature."""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create some sample videos
        self.watched_video = LanguageVideo.objects.create(
            user=self.user,
            title='Watched Spanish Video',
            youtube_id='abc123',
            language='spanish',
            level='beginner',
            video_type='lesson',
            duration='medium',
            is_watched=True
        )
        
        self.unwatched_video = LanguageVideo.objects.create(
            user=self.user,
            title='Unwatched Spanish Video',
            youtube_id='def456',
            language='spanish',
            level='beginner',
            video_type='lesson',
            duration='medium',
            is_watched=False
        )
        
        # Set up client and login
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_daily_video_recommendation(self):
        """Test that daily_video recommends an unwatched video."""
        response = self.client.get(reverse('videos:daily'), follow=True)
        
        # Should be redirected to the index with the unwatched video
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/index.html')
        
        # The current video should be the unwatched one
        video_id_param = response.request.get('QUERY_STRING')
        self.assertIn(f"video_id={self.unwatched_video.id}", video_id_param)
    
    def test_daily_video_all_watched(self):
        """Test the case when all videos have been watched."""
        # Mark all videos as watched
        self.unwatched_video.is_watched = True
        self.unwatched_video.save()
        
        response = self.client.get(reverse('videos:daily'), follow=True)
        
        # Should be redirected to the generator page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/index.html')
        
        # The URL should contain show_generator=true
        self.assertIn("show_generator=true", response.request.get('QUERY_STRING'))