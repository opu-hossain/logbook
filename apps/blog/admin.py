from django.contrib import admin
from .models import Post, Category, Comment

# Register models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "category", "created_at", "updated_at")
    list_filter = ("status", "category")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "created_at", "approved")
    list_filter = "approved"
    actions = "approve_comments"

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)

    approve_comments.short_description = "Approve selected comments"


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Comment)
