from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "views_count", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views_count", "helpful_count", "not_helpful_count", "created_at", "updated_at")
