# admin_files.py
"""
АДМИН-ПАНЕЛЬ ФАЙЛОВОГО МЕНЕДЖЕРА

Этот файл содержит кастомную админ-панель для управления файлами через модель ManagedFile.
Предоставляет полноценный файловый менеджер с возможностью:
- Просмотра и редактирования файлов
- Создания резервных копий
- Очистки содержимого
- Сканирования директорий
- Массовых операций с файлами

Файл вынесен отдельно от admin.py для избежания дублирования регистрации моделей.
"""

import mimetypes  # Модуль для определения MIME-типов файлов
import os  # Модуль для работы с операционной системой
import re  # Модуль для работы с регулярными выражениями
from datetime import datetime  # Класс для работы с датой и временем
from pathlib import Path  # Современный класс для работы с путями

from django.contrib import admin, messages  # Админка и система сообщений Django
from django.contrib.admin import SimpleListFilter  # Базовый класс для фильтров
from django.core.cache import cache  # Система кэширования Django
from django.db.models import Q  # Объекты для сложных запросов
from django.http import HttpResponseRedirect  # Класс для перенаправления
from django.shortcuts import get_object_or_404, render  # Функции для работы с запросами
from django.urls import path, reverse  # Функции для работы с URL
from django.utils.html import format_html, mark_safe  # Функции для безопасного HTML
from django.utils.translation import gettext_lazy as _  # Функция для перевода

from .models import ManagedFile  # Импорт модели управляемых файлов


class FileExistsFilter(SimpleListFilter):
    """
    Фильтр для отображения файлов по их существованию на диске.
    Позволяет фильтровать файлы: все, существующие, несуществующие.
    """

    title = _("Существует на диске")  # Заголовок фильтра
    parameter_name = "exists"  # Имя параметра в URL

    def lookups(self, request, model_admin):
        """
        Возвращает варианты выбора для фильтра.
        
        Возвращает:
            list: Список кортежей (значение, отображаемое имя)
        """
        return (
            ("yes", _("Существует")),  # Файлы, которые есть на диске
            ("no", _("Не существует")),  # Файлы, которых нет на диске
        )

    def queryset(self, request, queryset):
        """
        Фильтрует QuerySet в зависимости от выбранного значения.
        
        Параметры:
            request: Объект HTTP запроса
            queryset: Исходный QuerySet
            
        Возвращает:
            QuerySet: Отфильтрованный QuerySet
        """
        if self.value() == "yes":
            # Фильтруем файлы, которые существуют на диске
            return [obj for obj in queryset if obj.exists]
        elif self.value() == "no":
            # Фильтруем файлы, которые не существуют на диске
            return [obj for obj in queryset if not obj.exists]
        return queryset  # Если фильтр не выбран, возвращаем все


class TextFileFilter(SimpleListFilter):
    """
    Фильтр для отображения файлов по типу (текстовый/бинарный).
    """

    title = _("Тип файла")  # Заголовок фильтра
    parameter_name = "text_file"  # Имя параметра в URL

    def lookups(self, request, model_admin):
        """
        Возвращает варианты выбора для фильтра типа файла.
        
        Возвращает:
            list: Список кортежей (значение, отображаемое имя)
        """
        return (
            ("text", _("Текстовые")),  # Текстовые файлы
            ("binary", _("Бинарные")),  # Бинарные файлы
        )

    def queryset(self, request, queryset):
        """
        Фильтрует QuerySet по типу файла.
        
        Параметры:
            request: Объект HTTP запроса
            queryset: Исходный QuerySet
            
        Возвращает:
            QuerySet: Отфильтрованный QuerySet
        """
        if self.value() == "text":
            return queryset.filter(is_text_file=True)  # Текстовые файлы
        elif self.value() == "binary":
            return queryset.filter(is_text_file=False)  # Бинарные файлы
        return queryset  # Если фильтр не выбран, возвращаем все


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления файлами через веб-интерфейс.
    Предоставляет полный файловый менеджер с расширенными функциями.
    """

    # Поля для отображения в списке файлов
    list_display = [
        "name",  # Имя файла
        "category_display",  # Категория (отображаемое имя)
        "file_path_short",  # Укороченный путь
        "size_display",  # Размер в удобочитаемом формате
        "exists_display",  # Индикатор существования
        "mtime_display",  # Дата изменения
        "actions",  # Кнопки действий
    ]

    list_filter = [
        "category",  # Фильтр по категории
        "is_active",  # Фильтр по активности
        FileExistsFilter,  # Кастомный фильтр по существованию
        TextFileFilter,  # Кастомный фильтр по типу файла
    ]

    search_fields = [
        "name",  # Поиск по имени файла
        "file_path",  # Поиск по пути
        "description",  # Поиск по описанию
        "category",  # Поиск по категории
    ]

    readonly_fields = [
        "file_size",  # Размер файла (только чтение)
        "file_mtime",  # Время изменения (только чтение)
        "mime_type",  # MIME-тип (только чтение)
        "file_permissions",  # Права доступа (только чтение)
        "last_checked",  # Последняя проверка (только чтение)
        "created_at",  # Дата создания (только чтение)
    ]

    # Поля, которые можно редактировать в списке
    list_editable = ["is_active"]

    # Пагинация: 50 файлов на страницу
    list_per_page = 50

    # Поля, которые используются для автозаполнения
    prepopulated_fields = {"name": ("file_path",)}

    # Действия, доступные в выпадающем списке
    actions = [
        "refresh_file_info",  # Обновить информацию о файлах
        "create_backup",  # Создать резервные копии
        "clear_files",  # Очистить файлы
        "toggle_active",  # Переключить активность
        "scan_directory",  # Сканировать директорию
    ]

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": (
                    "name",  # Имя файла
                    "file_path",  # Полный путь
                    "category",  # Категория
                    "description",  # Описание
                    "is_active",  # Активность
                )
            },
        ),
        (
            _("Настройки файла"),
            {
                "fields": (
                    "is_text_file",  # Текстовый файл
                    "encoding",  # Кодировка
                    "auto_backup",  # Авто-бэкап
                    "max_backups",  # Макс. бэкапов
                ),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
        (
            _("Содержимое файла"),
            {
                "fields": ("content",),  # Содержимое
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
        (
            _("Информация о файле"),
            {
                "fields": (
                    "file_size",  # Размер
                    "file_mtime",  # Время изменения
                    "mime_type",  # MIME-тип
                    "file_permissions",  # Права доступа
                    "last_checked",  # Последняя проверка
                ),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
    )

    def get_urls(self):
        """
        Возвращает кастомные URL маршруты для админки.
        
        Добавляет маршруты для:
        - Просмотра содержимого файла
        - Очистки файла
        - Создания бэкапа
        - Обновления информации
        - Сканирования директории
        - Массовой очистки
        
        Возвращает:
            list: Список URL маршрутов
        """
        urls = super().get_urls()  # Получаем стандартные URL
        custom_urls = [
            # Просмотр содержимого файла
            path(
                "<path:object_id>/view/",
                self.admin_site.admin_view(self.view_file_content),
                name="main_managedfile_view",
            ),
            # Очистка одного файла
            path(
                "<path:object_id>/clear/",
                self.admin_site.admin_view(self.clear_file),
                name="main_managedfile_clear",
            ),
            # Создание бэкапа
            path(
                "<path:object_id>/backup/",
                self.admin_site.admin_view(self.create_file_backup),
                name="main_managedfile_backup",
            ),
            # Обновление информации
            path(
                "<path:object_id>/refresh/",
                self.admin_site.admin_view(self.refresh_file),
                name="main_managedfile_refresh",
            ),
            # Сканирование директории
            path(
                "scan-directory/",
                self.admin_site.admin_view(self.scan_directory_view),
                name="main_managedfile_scan",
            ),
            # Массовая очистка
            path(
                "clear-files/",
                self.admin_site.admin_view(self.clear_files_view),
                name="main_managedfile_clear_all",
            ),
        ]
        return custom_urls + urls  # Объединяем кастомные и стандартные URL

    def category_display(self, obj):
        """
        Возвращает отображаемое имя категории.
        
        Параметры:
            obj: Объект ManagedFile
            
        Возвращает:
            str: Отображаемое имя категории
        """
        return obj.get_category_display()
    category_display.short_description = _("Категория")  # Заголовок столбца

    def file_path_short(self, obj):
        """
        Возвращает укороченный путь к файлу для отображения.
        
        Параметры:
            obj: Объект ManagedFile
            
        Возвращает:
            str: Укороченный путь (максимум 50 символов)
        """
        if len(obj.file_path) > 50:
            return f"{obj.file_path[:47]}..."  # Обрезаем длинные пути
        return obj.file_path
    file_path_short.short_description = _("Путь")  # Заголовок столбца

    def size_display(self, obj):
        """
        Возвращает размер файла в удобочитаемом формате.
        
        Параметры:
            obj: Объект ManagedFile
            
        Возвращает:
            str: Размер с единицей измерения
        """
        return obj.human_readable_size
    size_display.short_description = _("Размер")  # Заголовок столбца

    def exists_display(self, obj):
        """
        Возвращает HTML-индикатор существования файла.
        
        Параметры:
            obj: Объект ManagedFile
            
        Возвращает:
            str: HTML-код индикатора (зеленый/красный)
        """
        if obj.exists:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                _("Существует"),
            )
        else:
            return format_html(
                '<span style="color: red;">✗ {}</span>',
                _("Не существует"),
            )
    exists_display.short_description = _("Статус")  # Заголовок столбца

    def mtime_display(self, obj):
        """
        Возвращает дату изменения файла в удобочитаемом формате.
        
        Параметры:
            obj: Объект ManagedFile
            
        Возвращает:
            str: Дата изменения или "Неизвестно"
        """
        if obj.file_mtime:
            return obj.file_mtime.strftime("%d.%m.%Y %H:%M")
        return _("Неизвестно")
    mtime_display.short_description = _("Изменен")  # Заголовок столбца

    def actions(self, obj):
        """
        Возвращает HTML-код кнопок действий для файла.
        
        Параметры:
            obj: Объект ManagedFile
            
        Возвращает:
            str: HTML-код с кнопками действий
        """
        buttons = []
        
        # Кнопка просмотра (только для текстовых файлов)
        if obj.exists and obj.is_text_file:
            view_url = reverse("admin:main_managedfile_view", args=[obj.pk])
            buttons.append(
                f'<a href="{view_url}" class="button" title="{_("Просмотр")}">👁️</a>'
            )
        
        # Кнопка обновления информации
        refresh_url = reverse("admin:main_managedfile_refresh", args=[obj.pk])
        buttons.append(
            f'<a href="{refresh_url}" class="button" title="{_("Обновить")}">🔄</a>'
        )
        
        # Кнопка создания бэкапа
        if obj.exists:
            backup_url = reverse("admin:main_managedfile_backup", args=[obj.pk])
            buttons.append(
                f'<a href="{backup_url}" class="button" title="{_("Бэкап")}">💾</a>'
            )
        
        # Кнопка очистки
        if obj.exists:
            clear_url = reverse("admin:main_managedfile_clear", args=[obj.pk])
            buttons.append(
                f'<a href="{clear_url}" class="button" title="{_("Очистить")}" '
                f'onclick="return confirm(\'{_("Очистить файл?")}\')">🗑️</a>'
            )
        
        return format_html(" ".join(buttons))
    actions.short_description = _("Действия")  # Заголовок столбца

    def view_file_content(self, request, object_id):
        """
        Отображает содержимое текстового файла.
        
        Параметры:
            request: Объект HTTP запроса
            object_id: ID файла
            
        Возвращает:
            HttpResponse: Страница с содержимым файла
        """
        file_obj = get_object_or_404(ManagedFile, pk=object_id)
        
        if not file_obj.exists:
            messages.error(request, _("Файл не существует на диске"))
            return HttpResponseRedirect(
                reverse("admin:main_managedfile_changelist")
            )
        
        if not file_obj.is_text_file:
            messages.warning(request, _("Файл не является текстовым"))
        
        context = {
            "title": _("Просмотр файла: {}").format(file_obj.name),
            "file": file_obj,
            "opts": self.model._meta,
            "content": file_obj.content,
            "lines": file_obj.content.count("\n") + 1 if file_obj.content else 0,
        }
        
        return render(request, "admin/main/view_file_content.html", context)

    def clear_file(self, request, object_id):
        """
        Очищает содержимое файла.
        
        Параметры:
            request: Объект HTTP запроса
            object_id: ID файла
            
        Возвращает:
            HttpResponseRedirect: Перенаправление обратно к списку
        """
        file_obj = get_object_or_404(ManagedFile, pk=object_id)
        
        success, message = file_obj.clear_file()
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return HttpResponseRedirect(
            reverse("admin:main_managedfile_changelist")
        )

    def create_file_backup(self, request, object_id):
        """
        Создает резервную копию файла.
        
        Параметры:
            request: Объект HTTP запроса
            object_id: ID файла
            
        Возвращает:
            HttpResponseRedirect: Перенаправление обратно к списку
        """
        file_obj = get_object_or_404(ManagedFile, pk=object_id)
        
        backup_path, message = file_obj.create_backup()
        if backup_path:
            messages.success(request, f"{message}: {os.path.basename(backup_path)}")
        else:
            messages.error(request, message)
        
        return HttpResponseRedirect(
            reverse("admin:main_managedfile_changelist")
        )

    def refresh_file(self, request, object_id):
        """
        Обновляет информацию о файле с диска.
        
        Параметры:
            request: Объект HTTP запроса
            object_id: ID файла
            
        Возвращает:
            HttpResponseRedirect: Перенаправление обратно к списку
        """
        file_obj = get_object_or_404(ManagedFile, pk=object_id)
        
        success, message = file_obj.refresh_file_info()
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return HttpResponseRedirect(
            reverse("admin:main_managedfile_changelist")
        )

    # Массовые действия
    def refresh_file_info(self, request, queryset):
        """
        Массовое действие: обновить информацию о выбранных файлах.
        
        Параметры:
            request: Объект HTTP запроса
            queryset: QuerySet выбранных файлов
        """
        count = 0
        for file_obj in queryset:
            success, _ = file_obj.refresh_file_info()
            if success:
                count += 1
        
        messages.success(
            request,
            _("Информация обновлена для {} файлов").format(count),
        )
    refresh_file_info.short_description = _("Обновить информацию о файлах")

    def create_backup(self, request, queryset):
        """
        Массовое действие: создать резервные копии выбранных файлов.
        
        Параметры:
            request: Объект HTTP запроса
            queryset: QuerySet выбранных файлов
        """
        count = 0
        for file_obj in queryset:
            if file_obj.exists:
                backup_path, _ = file_obj.create_backup()
                if backup_path:
                    count += 1
        
        messages.success(
            request,
            _("Резервные копии созданы для {} файлов").format(count),
        )
    create_backup.short_description = _("Создать резервные копии")

    def clear_files(self, request, queryset):
        """
        Массовое действие: очистить выбранные файлы.
        
        Параметры:
            request: Объект HTTP запроса
            queryset: QuerySet выбранных файлов
            
        Возвращает:
            HttpResponseRedirect: Перенаправление на страницу подтверждения
        """
        if request.POST.get("confirm"):
            # Если подтверждено, очищаем файлы
            count = 0
            for file_obj in queryset:
                if file_obj.exists:
                    success, _ = file_obj.clear_file()
                    if success:
                        count += 1
            
            messages.success(
                request,
                _("Очищено {} файлов").format(count),
            )
            return HttpResponseRedirect(
                reverse("admin:main_managedfile_changelist")
            )
        else:
            # Показываем страницу подтверждения
            context = {
                "title": _("Подтверждение очистки файлов"),
                "files": queryset,
                "opts": self.model._meta,
                "action_name": "clear_files",
            }
            return render(
                request,
                "admin/main/confirm_clear_files.html",
                context,
            )
    clear_files.short_description = _("Очистить файлы")

    def toggle_active(self, request, queryset):
        """
        Массовое действие: переключить активность выбранных файлов.
        
        Параметры:
            request: Объект HTTP запроса
            queryset: QuerySet выбранных файлов
        """
        for file_obj in queryset:
            file_obj.is_active = not file_obj.is_active
            file_obj.save()
        
        messages.success(
            request,
            _("Активность переключена для {} файлов").format(queryset.count()),
        )
    toggle_active.short_description = _("Переключить активность")

    def scan_directory_view(self, request):
        """
        Сканирует директорию и добавляет найденные файлы.
        
        Параметры:
            request: Объект HTTP запроса
            
        Возвращает:
            HttpResponse: Страница сканирования или результат сканирования
        """
        if request.method == "POST":
            directory = request.POST.get("directory", "").strip()
            file_pattern = request.POST.get("pattern", "*").strip()
            category = request.POST.get("category", "other")
            
            if not directory or not os.path.isdir(directory):
                messages.error(request, _("Укажите корректную директорию"))
                return HttpResponseRedirect(
                    reverse("admin:main_managedfile_scan")
                )
            
            # Сканируем директорию
            import glob
            pattern = os.path.join(directory, file_pattern)
            files_found = glob.glob(pattern, recursive=True)
            
            added_count = 0
            for file_path in files_found:
                if os.path.isfile(file_path):
                    # Проверяем, не добавлен ли уже этот файл
                    if not ManagedFile.objects.filter(file_path=file_path).exists():
                        file_name = os.path.basename(file_path)
                        ManagedFile.objects.create(
                            name=file_name,
                            file_path=file_path,
                            category=category,
                            is_active=True,
                        )
                        added_count += 1
            
            messages.success(
                request,
                _("Добавлено {} новых файлов").format(added_count),
            )
            return HttpResponseRedirect(
                reverse("admin:main_managedfile_changelist")
            )
        
        # GET запрос - показываем форму сканирования
        context = {
            "title": _("Сканирование директории"),
            "opts": self.model._meta,
        }
        return render(
            request,
            "admin/main/scan_directory.html",
            context,
        )

    def clear_files_view(self, request):
        """
        Массовая очистка всех файлов (через отдельную страницу).
        
        Параметры:
            request: Объект HTTP запроса
            
        Возвращает:
            HttpResponse: Страница подтверждения или результат очистки
        """
        if request.method == "POST":
            if request.POST.get("confirm"):
                # Очищаем все файлы
                files = ManagedFile.objects.filter(is_active=True)
                count = 0
                for file_obj in files:
                    if file_obj.exists:
                        success, _ = file_obj.clear_file()
                        if success:
                            count += 1
                
                messages.success(
                    request,
                    _("Очищено {} файлов").format(count),
                )
                return HttpResponseRedirect(
                    reverse("admin:main_managedfile_changelist")
                )
        
        # GET запрос - показываем страницу подтверждения
        files_count = ManagedFile.objects.filter(is_active=True).count()
        context = {
            "title": _("Массовая очистка файлов"),
            "files_count": files_count,
            "opts": self.model._meta,
        }
        return render(
            request,
            "admin/main/confirm_clear_all.html",
            context,
        )

    def save_model(self, request, obj, form, change):
        """
        Сохраняет модель с дополнительной логикой.
        
        Действия:
        1. Сохраняет модель через родительский метод
        2. Обновляет информацию о файле с диска
        3. Очищает кэш управляемых файлов
        
        Параметры:
            request: Объект HTTP запроса
            obj: Сохраняемый объект
            form: Форма с данными
            change: Флаг изменения существующего объекта
        """
        super().save_model(request, obj, form, change)
        
        # Обновляем информацию о файле
        obj.refresh_file_info()
        
        # Очищаем кэш
        cache.delete_many([
            "managed_files_list",
            "managed_files_active",
            "managed_files_stats",
        ])

    class Media:
        """
        Подключает кастомные CSS и JavaScript файлы.
        """
        css = {
            "all": (
                "css/badge.css",
                "css/admin-file-manager.css",
            )
        }
        js = ("js/admin-file-manager.js",)
