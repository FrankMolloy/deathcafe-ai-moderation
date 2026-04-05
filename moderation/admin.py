from django.contrib import admin
from .models import Post, ModerationResult


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "body")


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = ("post", "recommendation", "confidence", "model_name", "created_at")
    list_filter = ("recommendation", "created_at")