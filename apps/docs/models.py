from django.db import models
from django.conf import settings
from django.urls import translate_url
from django.utils.text import slugify

# Create your models here.


class Project(models.Model):
    class SyncStatus(models.TextChoices):
        PENDING = "pending", "Never synced"
        SYNCING = "syncing", "Syncing"
        SYNCED = "synced", "Synced"
        FAILED = "failed", "Failed"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doc_projects"
    )
    name = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    github_owner = models.CharField(max_length=200)
    github_repo = models.CharField(max_length=200)
    default_branch = models.CharField(max_length=100, default="main", blank=True)
    docs_path = models.CharField(max_length=200, default="docs", blank=True)
    is_public = models.BooleanField(
        default=False,
        help_text="Public docs are viewable by anyone with the link. Private docs are visible only to you.",
    )
    nav_tree = models.JSONField(default=list, blank=True)
    sync_status = models.CharField(
        max_length=10, choices=SyncStatus.choices, default=SyncStatus.PENDING
    )
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("github_owner", "github_repo")

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.github_repo
        if not self.slug:
            base_slug = slugify(self.name) or "project"
            unique_slug = base_slug
            counter = 1
            while Project.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                counter += 1
                unique_slug = f"{base_slug}-{counter}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def github_full_name(self):
        return f"{self.github_owner}/{self.github_repo}"

    def __str__(self):
        return self.name


class DocPage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pages")
    file_path = models.CharField(max_length=500)
    slug_path = models.CharField(max_length=500)
    title = models.CharField(max_length=200)
    nav_label = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    raw_markdown = models.TextField()
    github_sha = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "slug_path")
        ordering = ["order", "slug_path"]

    def __str__(self):
        return f"{self.project.slug}/{self.slug_path}"
