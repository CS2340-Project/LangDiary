from datetime import datetime, timedelta, date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, timedelta, date
import os

class DailyActivity(models.Model):
    """
    Model to track daily learning activity and streaks
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    completed_daily_goal = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'date']
        verbose_name_plural = "Daily Activities"
    
    def __str__(self):
        return f"{self.user.username}'s activity on {self.date}"
    
    @classmethod
    def mark_goal_completed(cls, user):
        """
        Mark today's goal as completed and update the user's streak
        """
        today = timezone.now().date()
        
        # Get or create today's activity
        activity, created = cls.objects.get_or_create(
            user=user,
            date=today,
            defaults={'completed_daily_goal': True}
        )
        
        if not created and not activity.completed_daily_goal:
            activity.completed_daily_goal = True
            activity.save()
        
        # Update the streak
        cls.update_streak(user)
        
        return activity
    
    @classmethod
    def update_streak(cls, user):
        """
        Update the user's learning streak based on activity history
        """
        profile = user.profile
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Check if the user completed today's goal
        today_activity = cls.objects.filter(user=user, date=today, completed_daily_goal=True).exists()
        
        if not today_activity:
            # Today's goal hasn't been completed yet, so don't update streak
            return profile.learning_streak
        
        # Check if yesterday's goal was completed
        yesterday_activity = cls.objects.filter(user=user, date=yesterday, completed_daily_goal=True).exists()
        
        if yesterday_activity or profile.learning_streak == 0:
            # If yesterday's goal was completed or this is the first day of the streak,
            # increment the streak
            profile.learning_streak += 1
        else:
            # Yesterday's goal was not completed, reset streak to 1 (for today)
            profile.learning_streak = 1
        
        profile.save()
        return profile.learning_streak
    
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
    exercises_completed = models.IntegerField(default=0)
    flashcards_completed = models.IntegerField(default=0)
    videos_completed = models.IntegerField(default=0)
    langlocale_activities_completed = models.IntegerField(default=0)
    
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
        ('upper intermediate', 'Upper Intermediate (B2)'),
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
    affects_streak = models.BooleanField(default=False, 
                                        help_text="Whether completing this goal counts toward the user's streak")

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
            'flashcards': 'flashcards',
            'videos': 'videos',
            'exercises': 'exercises',
            'langlocale_activities': 'LangLocale activities'
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
