from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    native_language = models.CharField(max_length=50, blank=True)
    learning_languages = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', default='profile_pics/default.jpg')
    bio = models.TextField(blank=True)
    
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
    
# Signal to create/update Profile when User is created/updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()