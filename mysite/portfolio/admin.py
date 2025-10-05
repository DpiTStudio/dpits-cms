# portfolio/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PortfolioCategory,
    PortfolioItem,
    Client,
    Order,
    OrderMessage,
    Review,
)


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "is_active", "works_count", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    def works_count(self, obj):
        return obj.portfolioitem_set.count()

    works_count.short_description = "Количество работ"


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "status",
        "project_date",
        "views",
        "created_at",
    ]
    list_filter = ["status", "category", "project_date", "created_at"]
    search_fields = ["title", "short_description", "content"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["views", "created_at", "updated_at"]
    date_hierarchy = "project_date"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["user", "company", "is_verified", "created_at"]
    list_filter = ["is_verified", "created_at"]
    search_fields = ["user__username", "user__email", "company"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "client",
        "title",
        "status",
        "priority",
        "budget",
        "created_at",
    ]
    list_filter = ["status", "priority", "created_at"]
    search_fields = ["title", "description", "client__user__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(OrderMessage)
class OrderMessageAdmin(admin.ModelAdmin):
    list_display = ["order", "user", "is_admin_message", "created_at"]
    list_filter = ["is_admin_message", "created_at"]
    search_fields = ["message", "order__title", "user__username"]
    readonly_fields = ["created_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["portfolio_item", "client", "rating", "is_approved", "created_at"]
    list_filter = ["rating", "is_approved", "created_at"]
    search_fields = [
        "title",
        "content",
        "client__user__username",
        "portfolio_item__title",
    ]
    readonly_fields = ["created_at"]
