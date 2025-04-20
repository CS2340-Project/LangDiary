from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import LanguageVideo
from .forms import VideoGeneratorForm

class LanguageVideoModelTest(TestCase):
    """Simple tests for the LanguageVideo model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.video = LanguageVideo.objects.create(
            user=self.user,
            title='Test Video',
            youtube_id='abc123',
            language='spanish',
            level='beginner',
            video_type='lesson',
            duration='medium',
            description='Test description'
        )
    
    def test_video_attributes(self):
        """Test that video attributes are saved correctly."""
        self.assertEqual(self.video.title, 'Test Video')
        self.assertEqual(self.video.youtube_id, 'abc123')
        self.assertEqual(self.video.language, 'spanish')
        self.assertEqual(self.video.level, 'beginner')
        self.assertFalse(self.video.is_watched)
        self.assertFalse(self.video.is_favorite)


class FormTest(TestCase):
    """Simple tests for the VideoGeneratorForm."""
    
    def test_form_valid(self):
        """Test that form validates with required fields."""
        form_data = {
            'language': 'spanish',
            'level': 'beginner'
        }
        form = VideoGeneratorForm(data=form_data)
        self.assertTrue(form.is_valid())


class ViewTest(TestCase):
    """Simple tests for the video views."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        self.video = LanguageVideo.objects.create(
            user=self.user,
            title='Test Video',
            youtube_id='abc123',
            language='spanish',
            level='beginner',
            video_type='lesson',
            duration='medium',
            description='Test description'
        )
    
    def test_index_view(self):
        """Test that the index view loads correctly."""
        response = self.client.get(reverse('videos:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/index.html')
    
    def test_mark_watched(self):
        """Test that a video can be marked as watched."""
        self.assertFalse(self.video.is_watched)
        
        # Make the AJAX request
        response = self.client.post(
            reverse('videos:mark_watched'), 
            {'video_id': self.video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Refresh from database and check if watched
        self.video.refresh_from_db()
        self.assertTrue(self.video.is_watched)
    
    def test_remove_video(self):
        """Test that a video can be removed."""
        # Make sure we have a video initially
        self.assertEqual(LanguageVideo.objects.count(), 1)
        
        # Make the AJAX request
        response = self.client.post(
            reverse('videos:remove_video'),
            {'video_id': self.video.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that video is removed
        self.assertEqual(LanguageVideo.objects.count(), 0)