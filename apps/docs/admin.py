from django.contrib import admin
from .models import Project, DocPage

# Register your models here.


class DocPageInline(admin.TabularInline):
    model = DocPage
    extra = 0
    fields = ("title", "slug_path", "order", "updated_at")
    readonly_fields = ("updated_at",)


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "github_full_name",
        "sync_status",
        "last_synced_at",
    )
    list_filter = ("sync_status",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [DocPageInline]


admin.site.register(Project, ProjectAdmin)
