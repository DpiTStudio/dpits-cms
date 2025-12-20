# accounts/admin.py
# Конфигурация административной панели для приложения аккаунтов

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, Ticket, TicketResponse


class UserProfileInline(admin.StackedInline):
    """
    Инлайн-редактор профиля пользователя прямо на странице редактирования User.
    """

    model = UserProfile
    can_delete = False  # Запрет удаления профиля отдельно от пользователя
    verbose_name_plural = "Профили"
    fields = ["phone", "avatar_preview", "avatar", "bio", "created_at", "updated_at"]
    readonly_fields = ["avatar_preview", "created_at", "updated_at"]

    def avatar_preview(self, obj):
        """Отображение миниатюры аватара в админке"""
        if obj and obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "Нет аватара"

    avatar_preview.short_description = "Превью аватара"


class UserAdmin(BaseUserAdmin):
    """
    Переопределенный класс управления пользователями с интеграцией профиля.
    """

    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Управление тикетами техподдержки в админке.
    """

    list_display = ["id", "user", "subject", "status", "created_at", "updated_at"]
    list_filter = ["status", "created_at"]
    list_editable = ["status"]  # Возможность менять статус прямо из списка
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["subject", "message", "user__username"]
    list_per_page = 20

    fieldsets = (
        ("Основная информация", {"fields": ("user", "subject", "message", "status")}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Оптимизация запросов через select_related"""
        return super().get_queryset(request).select_related("user")


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    """
    Управление ответами на тикеты.
    """

    list_display = [
        "id",
        "ticket",
        "user",
        "is_admin_response",
        "created_at",
        "message_preview",
    ]
    list_filter = ["is_admin_response", "created_at"]
    readonly_fields = ["created_at"]
    search_fields = ["message", "user__username", "ticket__subject"]
    list_per_page = 20

    fieldsets = (
        (
            "Информация об ответе",
            {"fields": ("ticket", "user", "message", "is_admin_response")},
        ),
        ("Дата", {"fields": ("created_at",)}),
    )

    def message_preview(self, obj):
        """Короткое превью текста сообщения для списка"""
        msg = getattr(obj, "message", "") or ""
        return (msg[:50] + "...") if len(msg) > 50 else msg

    message_preview.short_description = "Предпросмотр сообщения"

    def get_queryset(self, request):
        """Оптимизация запросов для списка ответов"""
        return super().get_queryset(request).select_related("ticket", "user")


# Перерегистрируем стандартную модель User с нашей новой конфигурацией
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
