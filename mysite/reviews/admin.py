# reviews/admin.py

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "status", "created_at"]
    list_filter = ["status", "created_at"]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Информация о пользователе", {"fields": ("full_name", "phone", "email")}),
        ("Отзыв", {"fields": ("message",)}),
        ("Статус", {"fields": ("status",)}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )
