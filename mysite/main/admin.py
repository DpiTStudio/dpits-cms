# admin.py

"""
АДМИН-ПАНЕЛЬ ДЛЯ МОДЕЛЕЙ ПРИЛОЖЕНИЯ MAIN

Этот файл регистрирует модели в админ-панели Django и настраивает их отображение.
Содержит кастомные классы ModelAdmin для каждой модели.

Основные функции:
1. SiteSettingsAdmin: Управление глобальными настройками сайта (singleton)
2. PageAdmin: Управление страницами сайта
3. LogStatsAdmin: Просмотр статистики лог-файлов (только чтение)

Примечание: ManagedFileAdmin находится в отдельном файле admin_files.py
для избежания дублирования регистрации и организации кода.
"""

import glob  # Модуль для работы с шаблонами путей к файлам (поиск по маскам)
import mimetypes  # Модуль для определения MIME-типов файлов
import os  # Модуль для работы с операционной системой (файлы, директории)
import stat  # Модуль для работы с правами доступа к файлам

from datetime import datetime  # Класс для работы с датой и временем
from django.conf import settings  # Настройки Django проекта
from django.contrib import (
    admin,  # Базовый класс админки Django
    messages,  # Система сообщений Django (уведомления пользователю)
)
from django.http import HttpResponseRedirect  # Класс для перенаправления HTTP-ответов
from django.shortcuts import (
    get_object_or_404,  # Функция для получения объекта или 404 ошибки
    render,  # Функция для рендеринга шаблонов
)

# ManagedFile импортируется в admin_files.py для избежания дублирования
from django.urls import path, reverse  # Функции для работы с URL
from django.utils.html import (
    format_html,  # Функция для безопасного форматирования HTML
    mark_safe,  # Функция для пометки строки как безопасного HTML
)
from django.utils.translation import gettext_lazy as _  # Функция для перевода строк

from .models import LogStats, Page, SiteSettings  # Импорт моделей для админки


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Админ-панель для настроек сайта.
    Обеспечивает singleton-режим (только одна запись настроек).
    """

    # Поля для отображения в списке записей
    list_display = ["slogan", "phone1", "email", "site_closed", "updated_at"]
    # Поля, которые отображаются в таблице списка объектов

    list_filter = ["site_closed"]  # Фильтры в правой панели
    # Поля, по которым можно фильтровать список

    readonly_fields = ["updated_at"]  # Только для чтения
    # Поля, которые нельзя редактировать в форме

    # Группировка полей по секциям
    fieldsets = (
        (
            _("Основная информация"),  # Заголовок секции
            {"fields": ("logo", "logo_text", "slogan", "motto", "short_description")},
            # Поля в этой секции
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
                # CSS класс для сворачивания/разворачивания секции
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
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        """
        Проверяет возможность добавления новых записей.

        Логика:
        - Разрешает создание только если записей еще нет
        - Запрещает создание дополнительных записей настроек

        Параметры:
            request: Объект HTTP запроса

        Возвращает:
            bool: True если можно добавить, False если нельзя
        """
        return not SiteSettings.objects.exists()
        # Разрешаем добавление только если нет ни одной записи

    def has_delete_permission(self, request, obj=None):
        """
        Проверяет возможность удаления записи.

        Логика:
        - Запрещает удаление единственной записи настроек

        Параметры:
            request: Объект HTTP запроса
            obj: Объект для удаления (опционально)

        Возвращает:
            bool: False (всегда запрещено)
        """
        return False  # Никогда не разрешаем удаление настроек

    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель с дополнительной логикой.

        Действия:
        1. Сохраняет модель через родительский метод
        2. Очищает кэш связанных данных

        Параметры:
            request: Объект HTTP запроса
            obj: Сохраняемый объект
            form: Форма с данными
            change: Флаг изменения существующего объекта

        Возвращает:
            None
        """
        super().save_model(
            request, obj, form, change
        )  # Вызываем стандартное сохранение

        # Очищаем кэш при сохранении настроек
        from django.core.cache import cache

        cache.delete("site_settings")  # Удаляем кэш настроек сайта
        cache.delete("menu_pages")  # Удаляем кэш меню
        cache.delete("featured_pages")  # Удаляем кэш рекомендуемых страниц


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
    # Поля, которые можно редактировать прямо в таблице без перехода к форме

    list_filter = ["show_in_menu", "show_on_site", "created_at"]  # Фильтры

    search_fields = ["title", "slug", "content"]  # Поля для поиска
    # Поля, по которым работает поисковая строка

    readonly_fields = ["created_at", "updated_at"]  # Только для чтения

    prepopulated_fields = {"slug": ("title",)}  # Автозаполнение slug из title
    # Поле slug автоматически заполняется на основе поля title

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

        Позволяет подключать кастомные CSS файлы к админ-панели.
        """

        css = {"all": ("admin/css/pages.css",)}
        # Подключаем CSS файл для стилизации админки страниц

    def get_queryset(self, request):
        """
        Возвращает QuerySet с оптимизацией запросов.

        Параметры:
            request: Объект HTTP запроса

        Возвращает:
            QuerySet: Оптимизированный QuerySet
        """
        return super().get_queryset(request)  # Используем стандартный QuerySet

    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель с дополнительной логикой.

        Действия:
        1. Сохраняет модель через родительский метод
        2. Очищает кэш связанных данных

        Параметры:
            request: Объект HTTP запроса
            obj: Сохраняемый объект
            form: Форма с данными
            change: Флаг изменения существующего объекта

        Возвращает:
            None
        """
        super().save_model(request, obj, form, change)

        # Очищаем кэш при сохранении страницы
        from django.core.cache import cache

        cache.delete("menu_pages")  # Удаляем кэш меню
        cache.delete("featured_pages")  # Удаляем кэш рекомендуемых страниц


@admin.register(LogStats)
class LogStatsAdmin(admin.ModelAdmin):
    """
    Админ-панель для статистики логов.

    Предоставляет интерфейс для просмотра статистики лог-файлов.
    Статистика собирается автоматически, ручное добавление запрещено.
    Включает кнопки для очистки лог-файла и просмотра полной статистики.
    """

    list_display = [
        "log_date",  # Дата логов
        "total_lines",  # Всего строк
        "error_count",  # Количество ошибок
        "warning_count",  # Количество предупреждений
        "info_count",  # Количество информационных сообщений
        "updated_at",  # Дата обновления
    ]
    # Поля, отображаемые в списке статистики

    list_filter = ["log_date"]  # Фильтр по дате

    readonly_fields = ["created_at", "updated_at"]  # Только для чтения
    # Эти поля нельзя редактировать

    search_fields = ["log_date"]  # Поле для поиска
    # Можно искать по дате

    date_hierarchy = "log_date"  # Иерархия по дате
    # Добавляет навигацию по датам вверху страницы

    fieldsets = (
        (
            _("Основная статистика"),  # Заголовок первой секции
            {
                "fields": (
                    "log_date",  # Дата
                    "total_lines",  # Всего строк
                )
            },
        ),
        (
            _("Статистика по категориям"),  # Заголовок второй секции
            {
                "fields": (
                    "error_count",  # Ошибки
                    "warning_count",  # Предупреждения
                    "info_count",  # Информационные
                    "debug_count",  # Отладочные
                    "other_count",  # Прочие
                )
            },
        ),
        (
            _("Мета-информация"),  # Заголовок третьей секции
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
            # Секция сворачивается по умолчанию
        ),
    )

    def has_add_permission(self, request):
        """
        Проверяет возможность добавления новых записей.

        Логика:
        - Запрещает добавление записей вручную
        - Статистика должна собираться автоматически

        Параметры:
            request: Объект HTTP запроса

        Возвращает:
            bool: False (всегда запрещено)
        """
        return False  # Не разрешаем ручное добавление статистики

    def has_delete_permission(self, request, obj=None):
        """
        Проверяет возможность удаления записи.

        Логика:
        - Разрешает удаление только суперпользователям

        Параметры:
            request: Объект HTTP запроса
            obj: Объект для удаления (опционально)

        Возвращает:
            bool: True если суперпользователь, False в противном случае
        """
        return request.user.is_superuser  # Только суперпользователи могут удалять

    def get_urls(self):
        """
        Возвращает кастомные URL маршруты для админки.

        Добавляет маршруты для:
        - Очистки лог-файла
        - Просмотра полной статистики из debug.log

        Возвращает:
            list: Список URL маршрутов
        """
        urls = super().get_urls()  # Получаем стандартные URL
        custom_urls = [
            # Очистка лог-файла
            path(
                "clear-log/",
                self.admin_site.admin_view(self.clear_log_file_view),
                name="main_logstats_clear",
            ),
            # Просмотр полной статистики
            path(
                "view-statistics/",
                self.admin_site.admin_view(self.view_log_statistics),
                name="main_logstats_view",
            ),
        ]
        return custom_urls + urls  # Объединяем кастомные и стандартные URL

    def changelist_view(self, request, extra_context=None):
        """
        Переопределяет стандартное представление списка для добавления кнопок.

        Добавляет кнопки "Очистить" и "Статистика" в интерфейс админки.

        Параметры:
            request: Объект HTTP запроса
            extra_context: Дополнительный контекст для шаблона

        Возвращает:
            HttpResponse: Ответ с рендером страницы списка
        """
        extra_context = extra_context or {}
        
        # Добавляем URL для кнопок
        clear_url = reverse("admin:main_logstats_clear")
        statistics_url = reverse("admin:main_logstats_view")
        
        # Создаем HTML для кнопок
        buttons_html = format_html(
            '<div style="margin: 10px 0;">'
            '<a href="{}" class="button" style="margin-right: 10px;" '
            'onclick="return confirm(\'Вы уверены, что хотите очистить лог-файл? Это действие нельзя отменить!\');">'
            '🗑️ Очистить лог-файл</a>'
            '<a href="{}" class="button">'
            '📊 Статистика</a>'
            '</div>',
            clear_url,
            statistics_url
        )
        
        extra_context["action_buttons"] = buttons_html
        
        return super().changelist_view(request, extra_context)

    def clear_log_file_view(self, request):
        """
        Обрабатывает очистку лог-файла debug.log.

        Действия:
        1. Вызывает функцию очистки из log_utils
        2. Создает резервную копию перед очисткой
        3. Показывает сообщение об успехе/ошибке
        4. Перенаправляет обратно к списку статистики

        Параметры:
            request: Объект HTTP запроса

        Возвращает:
            HttpResponseRedirect: Перенаправление обратно к списку
        """
        from .log_utils import clear_log_file

        success, message = clear_log_file()
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return HttpResponseRedirect(
            reverse("admin:main_logstats_changelist")
        )

    def view_log_statistics(self, request):
        """
        Отображает полную статистику из файла debug.log.

        Получает всю информацию из файла debug.log и отображает её:
        - Полная информация о файле (размер, количество строк, дата изменения)
        - Статистика по категориям (ERROR, WARNING, INFO, DEBUG, OTHER)
        - Все строки из файла debug.log

        Параметры:
            request: Объект HTTP запроса

        Возвращает:
            HttpResponse: Страница с полной статистикой
        """
        from .log_utils import (
            get_log_file_info,
            get_log_file_path,
        )

        # Получаем полную информацию о лог-файле
        log_info = get_log_file_info()
        
        # Получаем путь к файлу
        log_file_path = get_log_file_path()
        
        # Читаем все строки из файла (или последние 10000 для больших файлов)
        all_lines = []
        if log_file_path and os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    # Если файл очень большой, показываем последние 10000 строк
                    if len(lines) > 10000:
                        all_lines = lines[-10000:]
                        messages.warning(
                            request,
                            f"Файл содержит {len(lines)} строк. Показаны последние 10000 строк."
                        )
                    else:
                        all_lines = lines
            except Exception as e:
                messages.error(request, f"Ошибка чтения файла: {str(e)}")
                all_lines = []

        context = {
            "title": _("Полная статистика лог-файла debug.log"),
            "opts": self.model._meta,
            "log_info": log_info,
            "all_lines": all_lines,
            "total_lines_displayed": len(all_lines),
        }

        return render(
            request,
            "admin/main/logstats_statistics.html",
            context,
        )
