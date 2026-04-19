# admin.py
# НАСТРОЙКА ПАНЕЛИ АДМИНИСТРИРОВАНИЯ
#
# Этот файл регистрирует модели приложения в админке Django и настраивает их интерфейс.
# Также здесь определены кастомные представления для управления системными ресурсами и логами.

import os  # Модуль для работы с файловой системой
import shutil  # Модуль для копирования и перемещения файлов (бэкапы)
from django.contrib import admin  # Основной модуль админки
from django.contrib import messages  # Система уведомлений (успех/ошибка)
from django.http import HttpResponseRedirect  # Перенаправка пользователя
from django.shortcuts import render  # Отрисовка шаблонов
from django.urls import path, reverse  # Работа с URL
from django.utils.html import format_html  # Безопасный вывод HTML в админке
from django.utils.translation import gettext_lazy as _  # Перевод строк

# Импорт моделей
from .models import (
    SiteSettings,       # Настройки сайта
    Page,               # CMS страницы
    LogStats,           # Статистика логов
    ErrorLog,           # Прокси-модель лога ошибок
    StatisticsBanner,   # Баннеры счетчиков
    AppHeroSettings,    # Настройки Hero
    PaymentMethod,      # Способы оплаты
)

# Импорт утилит
from .admin_utils import (
    get_server_info,
    get_installed_apps_info,
    get_middleware_info,
    get_site_url,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Админка для глобальных настроек сайта.
    Реализует шаблон Singleton (только одна запись в БД).
    """
    
    # Запрещаем создавать более одной записи
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    # Запрещаем удалять единственную запись
    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        """При сохранении настроек очищаем кэш."""
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        keys = ["site_settings", "menu_pages", "featured_pages"]
        for key in keys:
            cache.delete(key)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "server-info/",
                self.admin_site.admin_view(self.server_info_view),
                name="server_info",
            ),
        ]
        return custom_urls + urls

    def server_info_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            "title": _("Информация о сервере"),
            "server_info": get_server_info(),
            "installed_apps": get_installed_apps_info(),
            "middleware": get_middleware_info(),
            "site_url": get_site_url(),
        }
        return render(request, "admin/main/server_info.html", context)

    # Группировка полей
    fieldsets = (
        (_("Основные данные"), {
            "fields": ("title", "logo", "company_name", "hero_background", "logo_text", "slogan", "motto"),
        }),
        (_("Домен"), {
            "fields": ("domain", "slogan_domain"),
        }),
        (_("Контактная информация"), {
            "fields": ("phone1", "phone2", "email", "address"),
        }),
        (_("Соц. сети и месс."), {
            "fields": (
                ("facebook"), ("icon_facebook"),
                ("instagram"), ("icon_instagram"),
                ("youtube"), ("icon_youtube"),
                ("rutube"), ("icon_rutube"),
                ("vk_video"), ("icon_vk_video"),
                ("telegram"), ("icon_telegram"),
                ("vk"), ("icon_vk"),
                ("ok"), ("icon_ok"),
                ("twitter"), ("icon_twitter"),
                ("pinterest"), ("icon_pinterest"),
                ("linkedin"), ("icon_linkedin"),
                ("threads"), ("icon_threads"),
                ("whatsapp"), ("icon_whatsapp"),
                ("viber"), ("icon_viber"),
                ("skype"), ("icon_skype"),
            ),
            "description": _("Укажите ссылки на страницы в соцсетях и иконки для них."),
        }),
        (_("Контент"), {
            "fields": ("short_description", "content"),
        }),
        (_("Статус сайта"), {
            "fields": ("site_closed", "closure_message"),
        }),
        (_("SEO оптимизация"), {
            "fields": ("seo_title", "seo_keywords", "seo_description"),
            "classes": ("collapse",),
        }),
        (_("Системная информация"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Админка для управления статическими страницами сайта."""
    
    # Поля, отображаемые в списке
    list_display = ("title", "slug", "show_in_menu", "show_on_site", "order")
    # Поля, которые можно редактировать прямо в списке
    list_editable = ("show_in_menu", "show_on_site", "order")
    # Автоматическая генерация slug (URL) из заголовка
    prepopulated_fields = {"slug": ("title",)}
    # Поля для поиска
    search_fields = ("title", "content", "slug")
    
    def save_model(self, request, obj, form, change):
        """Очистка кэша меню при изменении страниц."""
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        cache.delete("menu_pages")
        cache.delete("featured_pages")

    fieldsets = (
        (None, {"fields": ("title", "slug", "content")}),
        (_("Отображение"), {"fields": ("show_in_menu", "show_on_site", "order")}),
        (
            _("Hero-секция"),
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                    "hero_image",
                    "hero_is_active",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("SEO"),
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
                "classes": ("collapse",),
            },
        ),
        (_("Даты"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(AppHeroSettings)
class AppHeroSettingsAdmin(admin.ModelAdmin):
    """Админка для настройки общих баннеров разделов."""

    list_display = ("app_name", "hero_title", "hero_is_active")
    list_editable = ("hero_is_active",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "app_name",
                    "hero_title",
                    "hero_subtitle",
                    "hero_image",
                    "hero_is_active",
                )
            },
        ),
    )


@admin.register(LogStats)
class LogStatsAdmin(admin.ModelAdmin):
    """
    Админка для управления системными логами (debug.log).
    Позволяет мониторить ошибки и очищать журналы.
    """
    list_display = ("log_date", "total_lines", "error_count", "warning_count")
    readonly_fields = ("log_date", "total_lines", "error_count", "warning_count", "info_count", "debug_count", "other_count")

    # Запрещаем ручное добавление записей (они создаются системой)
    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        """Добавляет кнопки управления (Очистить, Анализ, Редактировать) в верхнюю часть списка."""
        extra_context = extra_context or {}
        
        # Генерируем URL для действий
        clear_url = reverse("admin:main_logstats_clear")
        statistics_url = reverse("admin:main_logstats_view")
        edit_url = reverse("admin:main_logstats_edit")

        # Формируем HTML кнопок с иконками
        buttons_html = format_html(
            '<div style="margin: 10px 0;">'
            '<a href="{}" class="button" style="margin-right: 10px;" '
            "onclick=\"return confirm('Вы уверены? Это очистит текущий debug.log');\">"
            "🗑️ Очистить основной лог</a>"
            '<a href="{}" class="button" style="margin-right: 10px;">📊 Полная статистика</a>'
            '<a href="{}" class="button">✏️ Редактор файла</a>'
            "</div>",
            clear_url, statistics_url, edit_url
        )
        extra_context["action_buttons"] = buttons_html
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        """Регистрирует дополнительные URL-маршруты для действий с логами."""
        urls = super().get_urls()
        custom_urls = [
            path("clear-log/", self.admin_site.admin_view(self.clear_log_file_view), name="main_logstats_clear"),
            path("view-statistics/", self.admin_site.admin_view(self.view_log_statistics), name="main_logstats_view"),
            path("edit-log/", self.admin_site.admin_view(self.edit_log_file_view), name="main_logstats_edit"),
        ]
        return custom_urls + urls

    def clear_log_file_view(self, request):
        """Представление для очистки debug.log через утилиту."""
        from .log_utils import clear_log_file
        success, message = clear_log_file()
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return HttpResponseRedirect(reverse("admin:main_logstats_changelist"))

    def view_log_statistics(self, request):
        """Страница с детальным статистическим разбором debug.log."""
        from .log_utils import get_log_file_info, get_recent_log_lines
        log_info = get_log_file_info()
        # Нормализуем ключ размера файла для совместимости с шаблоном
        log_info['file_size_human'] = log_info.get('human_size', '—')
        all_lines = get_recent_log_lines(count=200)

        context = {
            **self.admin_site.each_context(request),
            "title": _("Анализ debug.log"),
            "log_info": log_info,
            "all_lines": all_lines,
            "total_lines_displayed": len(all_lines),
            "opts": self.model._meta,
        }
        return render(request, "admin/main/logstats_statistics.html", context)

    def edit_log_file_view(self, request):
        """Веб-редактор для файла логов. Позволяет вносить правки прямо из админки."""
        from .log_utils import get_log_file_path, get_log_file_info
        log_path = get_log_file_path()

        if request.method == "POST":
            content = request.POST.get("content", "")
            try:
                # Создаем резервную копию перед сохранением изменений
                if log_path and os.path.exists(log_path):
                    shutil.copy2(log_path, log_path + ".bak")
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messages.success(request, _("Файл успешно сохранен"))
            except Exception as e:
                messages.error(request, _("Ошибка сохранения: %(err)s") % {"err": e})

        # Читаем содержимое файла для отображения в textarea
        file_content = ""
        if log_path and os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()

        log_info = get_log_file_info()
        log_info['file_size_human'] = log_info.get('human_size', '—')

        context = {
            **self.admin_site.each_context(request),
            "title": _("Редактирование debug.log"),
            "file_content": file_content,
            "log_file_path": log_path,
            "log_info": log_info,
            "opts": self.model._meta,
        }
        return render(request, "admin/main/edit_log_file.html", context)


@admin.register(ErrorLog)
class ErrorLogAdmin(LogStatsAdmin):
    """
    Специализированная админка для управления журналом критических ошибок (error.log).
    Наследует базовую логику LogStatsAdmin, переопределяя пути и действия.
    """
    
    def get_queryset(self, request):
        # Модель прокси используется только для интерфейса, записи в БД для нее не создаются вручную
        return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        """Добавляет кнопки управления специально для лога ошибок."""
        extra_context = extra_context or {}
        clear_url = reverse("admin:main_errorlog_clear")
        statistics_url = reverse("admin:main_errorlog_view")
        edit_url = reverse("admin:main_errorlog_edit")

        buttons_html = format_html(
            '<div style="margin: 10px 0;">'  
            '<a href="{}" class="button" style="background:#ba2121;margin-right:8px;" '
            "onclick=\"return confirm('Внимание! Это удалит все записи об ошибках. Продолжить?');\">"
            "🗑️ ОЧИСТИТЬ ЛОГ ОШИБОК</a>"
            '<a href="{}" class="button" style="margin-right:8px;">📊 Статистика ошибок</a>'
            '<a href="{}" class="button">✏️ Редактор файла</a>'
            "</div>",
            clear_url, statistics_url, edit_url
        )
        extra_context["action_buttons"] = buttons_html
        return admin.ModelAdmin.changelist_view(self, request, extra_context)

    def get_urls(self):
        """Переопределяет URL-маршруты для работы именно с error.log."""
        urls = admin.ModelAdmin.get_urls(self)
        custom_urls = [
            path("clear-log/", self.admin_site.admin_view(self.clear_error_log_view), name="main_errorlog_clear"),
            path("view-statistics/", self.admin_site.admin_view(self.view_error_log_statistics), name="main_errorlog_view"),
            path("edit-log/", self.admin_site.admin_view(self.edit_error_log_file_view), name="main_errorlog_edit"),
        ]
        return custom_urls + urls

    def clear_error_log_view(self, request):
        """Очистка error.log через специализированную утилиту."""
        from .log_utils import clear_error_log_file
        success, message = clear_error_log_file()
        msg_level = messages.SUCCESS if success else messages.ERROR
        messages.add_message(request, msg_level, message)
        return HttpResponseRedirect(reverse("admin:main_errorlog_changelist"))

    def view_error_log_statistics(self, request):
        """Отображение статистики по критическим ошибкам."""
        from .log_utils import get_error_log_file_info, get_error_log_recent_lines
        log_info = get_error_log_file_info()
        # Нормализуем ключ размера файла для совместимости с шаблоном
        log_info['file_size_human'] = log_info.get('human_size', '—')
        all_lines = get_error_log_recent_lines(count=200)

        context = {
            **self.admin_site.each_context(request),
            "title": _("Анализ error.log"),
            "log_info": log_info,
            "all_lines": all_lines,
            "total_lines_displayed": len(all_lines),
            "opts": self.model._meta,
        }
        return render(request, "admin/main/errorlog_statistics.html", context)

    def edit_error_log_file_view(self, request):
        """Веб-редактор для файла error.log. Позволяет вносить правки прямо из админки."""
        from .log_utils import get_error_log_file_path, get_error_log_file_info
        log_path = get_error_log_file_path()

        if request.method == "POST":
            content = request.POST.get("content", "")
            try:
                if log_path and os.path.exists(log_path):
                    shutil.copy2(log_path, log_path + ".bak")
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messages.success(request, _("Файл error.log успешно сохранен"))
            except Exception as e:
                messages.error(request, _("Ошибка сохранения: %(err)s") % {"err": e})

        file_content = ""
        if log_path and os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()

        log_info = get_error_log_file_info()
        log_info['file_size_human'] = log_info.get('human_size', '—')

        context = {
            **self.admin_site.each_context(request),
            "title": _("Редактирование error.log"),
            "file_content": file_content,
            "log_file_path": log_path,
            "log_info": log_info,
            "opts": self.model._meta,
        }
        return render(request, "admin/main/edit_error_log_file.html", context)


@admin.register(StatisticsBanner)
class StatisticsBannerAdmin(admin.ModelAdmin):
    """
    Админка для управления внешними счетчиками и баннерами (Яндекс.Метрика, Google Analytics и др.).
    Позволяет гибко настраивать место и условия отображения кода.
    """
    
    list_display = ('name', 'banner_type', 'position', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('banner_type', 'position', 'is_active')
    search_fields = ('name', 'code', 'counter_id')
    
    # Группировка настроек по логическим блокам
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'banner_type', 'counter_id', 'description'),
            'description': 'Базовая информация о счетчике'
        }),
        ('Код (HTML/JS)', {
            'fields': ('code',), 
            'classes': ('wide',),
            'description': 'Вставьте сюда JS-код, предоставленный сервисом статистики'
        }),
        ('Отображение', {
            'fields': ('position', 'order', 'is_active'),
            'description': 'Где и в каком порядке выводить баннер'
        }),
        ('Где показывать', {
            'fields': ('show_on_all_pages', 'show_on_index', 'show_on_pages', 'show_on_news', 'show_on_portfolio'),
            'classes': ('collapse',),
            'description': 'Настройка видимости на конкретных разделах сайта'
        }),
        ('Для кого показывать', {
            'fields': ('enabled_for_admin', 'enabled_for_staff', 'enabled_for_users'),
            'classes': ('collapse',),
            'description': 'Настройка прав доступа для разных групп пользователей'
        }),
    )

# Импортируем админку файлов из отдельного модуля
try:
    from . import admin_files
except ImportError:
    pass

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('name',)