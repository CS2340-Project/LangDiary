from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LanguageVideo(models.Model):
    # Use the same language choices as in Profile model
    LANGUAGE_CHOICES = [
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    VIDEO_TYPE_CHOICES = [
        ('lesson', 'Lesson'),
        ('conversation', 'Conversation'),
        ('music', 'Music'),
        ('vlog', 'Vlog'),
        ('movie_clip', 'Movie Clip'),
        ('news', 'News'),
        ('interview', 'Interview'),
    ]
    
    DURATION_CHOICES = [
        ('short', 'Short (< 5 min)'),
        ('medium', 'Medium (5-15 min)'),
        ('long', 'Long (> 15 min)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_videos')
    title = models.CharField(max_length=255)
    youtube_id = models.CharField(max_length=20)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPE_CHOICES)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    is_watched = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title