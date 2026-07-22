from enum import unique
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField

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

    class ContentType(models.TextChoices):
        MARKDOWN = "markdown", "Markdown"
        HTML = "html", "Rich HTML"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    body = MarkdownxField()

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
            base_slug = slugify(self.title) or "untitled"
            unique_slug = base_slug
            counter = 1
            while Post.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                counter += 1
                unique_slug = f"{base_slug}-{counter}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.get_author_name()} on {self.post.title}"

    def get_author_name(self):
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.name
