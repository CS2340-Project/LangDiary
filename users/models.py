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
    
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_value = models.FloatField()
    current_value = models.FloatField()
    unit = models.CharField(max_length=50)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def progress_percentage(self):
        if self.target_value == 0:
            return "0%"
        percent = (self.current_value / self.target_value) * 100
        return f"{percent:.0f}%"
    progress_percentage.short_description = "Progress"

    def is_completed(self):
        return self.current_value >= self.target_value

    is_completed.boolean = True

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


class Place(models.Model):
    placeId = models.CharField(max_length=250)
    placeImageUrl = models.URLField()
    placeName = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.placeName} ({self.placeId[:15]}...)"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'place')

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

# Signal to create/update Profile when User is created/updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()