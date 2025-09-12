# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Ticket, TicketResponse


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Профили"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["user", "subject", "status", "created_at"]
    list_filter = ["status", "created_at"]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Информация о тикете", {"fields": ("user", "subject", "message", "status")}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ["ticket", "user", "is_admin_response", "created_at"]
    list_filter = ["is_admin_response", "created_at"]
    readonly_fields = ["created_at"]
    fieldsets = (
        (
            "Информация об ответе",
            {"fields": ("ticket", "user", "message", "is_admin_response")},
        ),
        ("Дата", {"fields": ("created_at",)}),
    )


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
