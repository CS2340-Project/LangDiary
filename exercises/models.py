from django.db import models
from datetime import date
from django.contrib.auth.models import User
# Create your models here.
class Exercise(models.Model):
    EXERCISE_TYPES = [('email', 'email'), ('story','story'), ('journal','journal')]
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner (A1)'),
        ('elementary', 'Elementary (A2)'),
        ('intermediate', 'Intermediate (B1)'),
        ('upper intermediate', 'Upper Intermediate (B2)'),
        ('advanced', 'Advanced (C1)'),
        ('proficient', 'Proficient (C2)'),
    ]
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, blank=True, choices=EXERCISE_TYPES)
    prompt = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    deadline = models.DateField()
    skill = models.CharField(max_length=250, blank=True, choices=SKILL_LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    days_left = models.IntegerField(default=99)
    editable = models.BooleanField(default=True)
    init = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)
    def __str__(self):
        return self.type + " " + str(self.deadline) + " " + self.content + " " + str(self.init)