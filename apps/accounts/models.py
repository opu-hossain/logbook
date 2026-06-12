from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    editor_preference = models.CharField(
        max_length=10,
        choices=[("html", "Visual editor"), ("markdown", "Markdown")],
        default="html",
    )

    def __str__(self):
        return self.username
