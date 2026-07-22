from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username


class GitHubAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="github_account",
    )
    github_id = models.BigIntegerField(unique=True)
    github_username = models.CharField(max_length=200)
    access_token = models.CharField(max_length=500)  # encrypted at rest, see crypto.py
    scope = models.CharField(max_length=200, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)

    def set_token(self, raw_token):
        from .crypto import encrypt_token

        self.access_token = encrypt_token(raw_token)

    @property
    def token(self):
        from .crypto import decrypt_token

        return decrypt_token(self.access_token)

    def __str__(self):
        return f"@{self.github_username} ({self.user})"
