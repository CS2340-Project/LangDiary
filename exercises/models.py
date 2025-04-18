from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Exercise(models.Model):
    EXERCISE_TYPES = [('email', 'email'), ('story','story'), ('journal','journal')]
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, blank=True, choices=EXERCISE_TYPES)
    content = models.TextField()
    deadline = models.DateField()
    def __str__(self):
        return self.type + " " + str(self.deadline) + " " + self.content