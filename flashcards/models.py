from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Flashcard(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    front_text = models.TextField()
    back_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_revisions = models.IntegerField(default=0)

    class Meta:
        ordering = ['num_revisions', 'updated_at']

    def __str__(self):
        return self.front_text + " " + self.back_text + " " + str(self.num_revisions)