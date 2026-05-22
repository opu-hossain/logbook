from django.contrib import admin
from .models import Post, Category

# Register models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "category", "created_at", "updated_at")
    list_filter = ("status", "category")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
