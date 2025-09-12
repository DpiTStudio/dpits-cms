# portfolio/admin.py

from django.contrib import admin
from .models import PortfolioCategory, Portfolio


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "show_in_menu", "order", "is_active"]
    list_editable = ["show_in_menu", "order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "image", "description")}),
        ("Настройки отображения", {"fields": ("show_in_menu", "order", "is_active")}),
    )


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "price", "can_order", "views", "is_active"]
    list_filter = ["category", "can_order", "is_active"]
    list_editable = ["price", "can_order", "is_active"]
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
        ("Цена и заказы", {"fields": ("price", "can_order")}),
        ("Статистика", {"fields": ("views", "created_at", "updated_at")}),
        ("SEO настройки", {"fields": ("seo_title", "seo_keywords", "seo_description")}),
        ("Статус", {"fields": ("is_active",)}),
    )
