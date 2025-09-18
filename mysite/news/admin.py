# news/admin.py

from django.contrib import admin
from .models import NewsCategory, News


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "show_in_menu", "order", "is_active"]
    list_editable = ["show_in_menu", "order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "image", "description")}),
        ("Настройки отображения", {"fields": ("show_in_menu", "order", "is_active")}),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "views", "is_active", "created_at"]
    list_filter = ["category", "is_active", "created_at"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["views", "created_at", "updated_at"]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "image",
                    "short_description",
                    "content",
                )
            },
        ),
        ("Статистика", {"fields": ("views", "created_at", "updated_at")}),
        ("SEO настройки", {"fields": ("seo_title", "seo_keywords", "seo_description")}),
        ("Статус", {"fields": ("is_active",)}),
    )
