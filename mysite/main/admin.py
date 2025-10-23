# admin.py
# Админ-панель для моделей приложения main
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Админ-панель для настроек сайта.
    Обеспечивает singleton-режим (только одна запись настроек).
    """

    # Поля для отображения в списке записей
    list_display = ["slogan", "phone1", "email", "site_closed", "updated_at"]
    list_filter = ["site_closed"]  # Фильтры в правой панели
    readonly_fields = ["updated_at"]  # Только для чтения

    # Группировка полей по секциям
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("logo", "logo_text", "slogan", "motto", "short_description")},
        ),
        (
            _("Контактная информация"),
            {"fields": ("phone1", "phone2", "email", "address")},
        ),
        (
            _("Социальные сети"),
            {
                "fields": (
                    "facebook",
                    "instagram",
                    "youtube",
                    "rutube",
                    "vk_video",
                    "telegram",
                    "vk",
                    "ok",
                ),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
        (
            _("Статус сайта"),
            {"fields": ("site_closed", "closure_message", "updated_at")},
        ),
        (
            _("Дополнительный контент"),
            {"fields": ("content",), "classes": ("collapse",)},
        ),
        (
            _("SEO оптимизация"),
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
    )

    def has_add_permission(self, request):
        """
        Запрещает создание дополнительных записей настроек.
        Разрешает создание только если записей еще нет.
        """
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """
        Запрещает удаление единственной записи настроек.
        """
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Админ-панель для страниц сайта.
    Предоставляет управление страницами с SEO-настройками.
    """

    # Поля для отображения в списке
    list_display = [
        "title",
        "slug",
        "show_in_menu",
        "show_on_site",
        "order",
        "updated_at",
    ]
    list_editable = [
        "show_in_menu",
        "show_on_site",
        "order",
    ]  # Редактируемые поля в списке
    list_filter = ["show_in_menu", "show_on_site", "created_at"]  # Фильтры
    search_fields = ["title", "slug", "content"]  # Поля для поиска
    readonly_fields = ["created_at", "updated_at"]  # Только для чтения
    prepopulated_fields = {"slug": ("title",)}  # Автозаполнение slug из title

    # Группировка полей
    fieldsets = (
        (_("Основное содержимое"), {"fields": ("title", "slug", "content")}),
        (
            _("Настройки отображения"),
            {"fields": ("show_in_menu", "show_on_site", "order")},
        ),
        (
            _("SEO оптимизация"),
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
        (
            _("Мета-информация"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        """
        Дополнительные CSS стили для админки.
        """

        css = {"all": ("admin/css/pages.css",)}
