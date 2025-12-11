# admin.py
# Админ-панель для моделей приложения main
# Предоставляет интерфейс управления настройками сайта, страницами и файлами
import os  # Модуль для работы с операционной системой
from django.contrib import admin  # Базовый класс админки Django
from django.utils.translation import gettext_lazy as _  # Функция для перевода строк
from .models import SiteSettings, Page, LogStats  # Импорт моделей для админки

# ManagedFile импортируется в admin_files.py для избежания дублирования
from django.urls import path, reverse  # Функции для работы с URL
from django.http import HttpResponseRedirect  # Класс для перенаправления HTTP-ответов
from django.contrib import messages  # Система сообщений Django
from django.utils.html import (
    format_html,
    mark_safe,
)  # Функции для безопасного форматирования HTML
from django.shortcuts import (
    render,
    get_object_or_404,
)  # Функции для работы с представлениями
from django.conf import settings  # Настройки Django проекта
import glob  # Модуль для работы с шаблонами путей к файлам
import stat  # Модуль для работы с правами доступа к файлам
import mimetypes  # Модуль для определения MIME-типов файлов
from datetime import datetime  # Класс для работы с датой и временем


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
        Проверяет возможность добавления новых записей.
        Запрещает создание дополнительных записей настроек.
        Разрешает создание только если записей еще нет.
        """
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """
        Проверяет возможность удаления записи.
        Запрещает удаление единственной записи настроек.
        """
        return False

    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель с дополнительной логикой.
        Переопределяет сохранение для очистки кэша.
        """
        super().save_model(request, obj, form, change)
        # Очищаем кэш при сохранении
        from django.core.cache import cache

        cache.delete("site_settings")
        cache.delete("menu_pages")
        cache.delete("featured_pages")


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

    def get_queryset(self, request):
        """
        Возвращает QuerySet с оптимизацией запросов.
        """
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель с дополнительной логикой.
        """
        super().save_model(request, obj, form, change)
        # Очищаем кэш при сохранении
        from django.core.cache import cache

        cache.delete("menu_pages")
        cache.delete("featured_pages")


# admin.py (добавляем после PageAdmin)
@admin.register(LogStats)
class LogStatsAdmin(admin.ModelAdmin):
    """
    Админ-панель для статистики логов.
    """

    list_display = [
        "log_date",
        "total_lines",
        "error_count",
        "warning_count",
        "info_count",
        "updated_at",
    ]
    list_filter = ["log_date"]
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["log_date"]
    date_hierarchy = "log_date"

    fieldsets = (
        (
            _("Основная статистика"),
            {
                "fields": (
                    "log_date",
                    "total_lines",
                )
            },
        ),
        (
            _("Статистика по категориям"),
            {
                "fields": (
                    "error_count",
                    "warning_count",
                    "info_count",
                    "debug_count",
                    "other_count",
                )
            },
        ),
        (
            _("Мета-информация"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request):
        """
        Запрещает добавление записей вручную.
        Статистика должна собираться автоматически.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Разрешает удаление только суперпользователям.
        """
        return request.user.is_superuser
