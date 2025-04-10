from django.db import models
from users.models import User

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
