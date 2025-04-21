# models.py
from django.db import models
from django.contrib.auth.models import User
from google.oauth2.credentials import Credentials
import json

class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_uri = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = models.TextField()

    def to_credentials(self):
        return Credentials(
            token=self.token,
            refresh_token=self.refresh_token,
            token_uri=self.token_uri,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=json.loads(self.scopes),
        )