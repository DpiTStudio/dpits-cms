# portfolio/admin.py
from django.contrib import admin
from .models import *


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["user", "company", "phone", "is_verified", "created_at"]
    list_filter = ["is_verified", "created_at"]
    list_editable = ["is_verified"]
    search_fields = ["user__username", "user__email", "company"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]
    list_display_links = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "description")}),
        ("Настройки отображения", {"fields": ("order", "is_active")}),
        ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords")}),
    )


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "client", "status", "project_date", "views"]
    list_filter = ["category", "status", "project_date"]
    list_editable = ["status"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["views", "created_at", "updated_at"]
    search_fields = ["title", "short_description"]
    date_hierarchy = "project_date"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "client", "title", "status", "priority", "budget", "deadline"]
    list_filter = ["status", "priority", "created_at"]
    list_editable = ["status", "priority"]
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["title", "client__user__username"]


@admin.register(OrderMessage)
class OrderMessageAdmin(admin.ModelAdmin):
    list_display = ["order", "user", "is_admin_message", "created_at"]
    list_filter = ["is_admin_message", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["client", "portfolio_item", "rating", "is_approved", "created_at"]
    list_filter = ["rating", "is_approved", "created_at"]
    list_editable = ["is_approved"]
    readonly_fields = ["created_at"]
