from asyncio import sleep
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from taggit.managers import TaggableManager

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"
        ARCHIVED = "AR", "Archived"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    body = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )

    tags = TaggableManager(blank=True)
    featured_image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta_description = models.CharField(
        max_length=160,
        blank=True,
        null=True,
        help_text="SEO description -> max 160 characters",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
