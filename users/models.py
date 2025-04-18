from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class Profile(models.Model):
    # Core fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics', default='profile_pics/default.jpg')
    bio = models.TextField(blank=True)
    exercise_ready = models.BooleanField(default=True)
    last_exercise_date = models.DateField(null=True, blank=True)
    
    # Language settings
    LANGUAGE_CHOICES = [
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
    ]
    
    LANGUAGE_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    # Language learning fields
    native_language = models.CharField(max_length=50, blank=True)
    language_learning = models.CharField(max_length=50, blank=True, choices=LANGUAGE_CHOICES)
    language_level = models.CharField(max_length=50, blank=True, choices=LANGUAGE_LEVEL_CHOICES)
    learning_goals = models.TextField(blank=True)
    
    # Progress tracking
    learning_streak = models.IntegerField(default=0)
    learning_progress = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    practice_minutes = models.IntegerField(default=0)
    
    # Study preferences
    pref_reading = models.BooleanField(default=False)
    pref_writing = models.BooleanField(default=False)
    pref_speaking = models.BooleanField(default=False)
    pref_listening = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def delete_profile_picture(self):
        """Delete profile picture and reset to default"""
        if self.profile_picture and self.profile_picture.name != 'profile_pics/default.jpg':
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
            self.profile_picture = 'profile_pics/default.jpg'
            self.save()
            return True
        return False

class UserPreferences(models.Model):
    COMMITMENT_CHOICES = [
        ('casual', 'Casual (5-10 minutes)'),
        ('regular', 'Regular (15-20 minutes)'),
        ('dedicated', 'Dedicated (30+ minutes)'),
        ('intense', 'Intense (60+ minutes)'),
    ]

    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner (A1)'),
        ('elementary', 'Elementary (A2)'),
        ('intermediate', 'Intermediate (B1)'),
        ('upper_intermediate', 'Upper Intermediate (B2)'),
        ('advanced', 'Advanced (C1)'),
        ('proficient', 'Proficient (C2)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    commitment_level = models.CharField(max_length=20, choices=COMMITMENT_CHOICES)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES)

    # Store lists as comma-separated strings
    goals = models.CharField(max_length=255, blank=True)
    areas = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

    def get_goals_list(self):
        return self.goals.split(',') if self.goals else []

    def set_goals_list(self, goals_list):
        self.goals = ','.join(goals_list)

    def get_areas_list(self):
        return self.areas.split(',') if self.areas else []

    def set_areas_list(self, areas_list):
        self.areas = ','.join(areas_list)

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_value = models.FloatField()
    current_value = models.FloatField()
    unit = models.CharField(max_length=50)
    deadline = models.DateField(default=datetime.now().date() + timedelta(days=3))
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(int((self.current_value / self.target_value) * 100), 100)

    @property
    def is_completed(self):
        return self.current_value >= self.target_value

    def __str__(self):
        return f"{self.title} - {self.user.username}"


    @property
    def formatted_unit(self):
        """Return a properly formatted version of the unit for display"""
        units = {
            'lessons': 'lessons',
            'minutes': 'minutes', 
            'days': 'days',
            'words': 'words',
            'exercises': 'exercises'
        }
        return units.get(self.unit, self.unit)



# Signal to create/update Profile when User is created/updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
