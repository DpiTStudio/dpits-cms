# admin.py
# Админ-панель для моделей приложения main
import os
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page, ManagedFile
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.html import format_html, mark_safe
from django.core.exceptions import PermissionDenied
from datetime import datetime


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

    def save_model(self, request, obj, form, change):
        """
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
        Оптимизирует запросы к базе данных.
        """
        qs = super().get_queryset(request)
        return qs.select_related()

    def save_model(self, request, obj, form, change):
        """
        Переопределяет сохранение для логирования изменений.
        """
        super().save_model(request, obj, form, change)
        # Очищаем кэш при сохранении
        from django.core.cache import cache

        cache.delete("menu_pages")
        cache.delete("featured_pages")


class ManagedFileAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления файлами через интерфейс администратора.
    Позволяет просматривать, редактировать и управлять файлами на диске.
    """

    list_display = [
        "name_display",
        "category_display",
        "file_path_short",
        "size_display",
        "status_display",
        "last_modified_display",
        "actions_column",
    ]

    list_filter = [
        "category",
        "is_active",
        "is_text_file",
        "auto_backup",
    ]

    search_fields = [
        "name",
        "file_path",
        "description",
        "content",
    ]

    readonly_fields = [
        "file_size",
        "file_mtime",
        "mime_type",
        "last_checked",
        "created_at",
        "file_info_display",
        "file_preview_display",
        "backups_list_display",
        "current_permissions",
    ]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "file_path",
                    "category",
                    "description",
                    "is_active",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Настройки управления",
            {
                "fields": (
                    "is_text_file",
                    "encoding",
                    "auto_backup",
                    "max_backups",
                ),
                "classes": ("wide",),
            },
        ),
        (
            "Содержимое файла",
            {
                "fields": ("content",),
                "description": "⚠️ Изменения сохраняются непосредственно в файл на диске!",
                "classes": ("wide",),
            },
        ),
        (
            "Информация о файле",
            {
                "fields": (
                    "file_info_display",
                    "file_preview_display",
                    "current_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Резервные копии",
            {
                "fields": ("backups_list_display",),
                "classes": ("collapse",),
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "file_size",
                    "file_mtime",
                    "mime_type",
                    "last_checked",
                    "created_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "refresh_selected_files",
        "create_backup_selected",
        "clear_selected_files",
        "toggle_active_selected",
        "scan_logs_directory",
    ]

    change_form_template = "admin/main/managedfile_change_form.html"
    change_list_template = "admin/main/managedfile_change_list.html"

    # Настройки для списка
    list_per_page = 25
    show_full_result_count = True

    def name_display(self, obj):
        """Отображение имени файла с иконкой"""
        icon = "📄" if obj.is_text_file else "💾"
        return format_html("<strong>{} {}</strong>", icon, obj.name)

    name_display.short_description = "Имя файла"
    name_display.admin_order_field = "name"

    def category_display(self, obj):
        """Отображение категории файла с цветным значком"""
        colors = {
            "log": "warning",
            "config": "info",
            "template": "primary",
            "static": "success",
            "media": "secondary",
            "database": "danger",
            "backup": "dark",
            "other": "light",
        }
        color = colors.get(obj.category, "light")

        return format_html(
            '<span class="badge badge-{}">{}</span>', color, obj.get_category_display()
        )

    category_display.short_description = "Категория"
    category_display.admin_order_field = "category"

    def file_path_short(self, obj):
        """Сокращенный путь к файлу для отображения в списке"""
        path = obj.file_path
        if len(path) > 40:
            return f"...{path[-40:]}"
        return path

    file_path_short.short_description = "Путь"
    file_path_short.admin_order_field = "file_path"

    def size_display(self, obj):
        """Отображение размера файла с цветным индикатором"""
        if obj.exists:
            color = (
                "success" if obj.file_size < 1024 * 1024 else "warning"
            )  # зеленый до 1MB, желтый больше
            return format_html(
                '<span class="badge badge-{}">{}</span>', color, obj.human_readable_size
            )
        return format_html('<span class="badge badge-danger">N/A</span>')

    size_display.short_description = "Размер"
    size_display.admin_order_field = "file_size"

    def status_display(self, obj):
        """Отображение статуса файла (активен/неактивен/отсутствует)"""
        if obj.exists:
            if obj.is_active:
                return format_html('<span class="badge badge-success">Активен</span>')
            else:
                return format_html(
                    '<span class="badge badge-secondary">Неактивен</span>'
                )
        else:
            return format_html('<span class="badge badge-danger">Отсутствует</span>')

    status_display.short_description = "Статус"

    def last_modified_display(self, obj):
        """Отображение времени последнего изменения файла в удобном формате"""
        if obj.file_mtime:
            from django.utils import timezone

            now = timezone.now()
            diff = now - obj.file_mtime

            if diff.days == 0:
                if diff.seconds < 60:
                    return "только что"
                elif diff.seconds < 3600:
                    return f"{diff.seconds // 60} мин назад"
                else:
                    return f"{diff.seconds // 3600} ч назад"
            elif diff.days == 1:
                return "вчера"
            elif diff.days < 7:
                return f"{diff.days} дн назад"
            else:
                return obj.file_mtime.strftime("%d.%m.%Y")
        return "—"

    last_modified_display.short_description = "Изменен"
    last_modified_display.admin_order_field = "file_mtime"

    def actions_column(self, obj):
        """Колонка с кнопками действий для файла"""
        buttons = []

        # Кнопка просмотра
        if obj.exists:
            buttons.append(
                format_html(
                    '<a href="{}" class="btn btn-sm btn-info mr-1" target="_blank" '
                    'title="Открыть в новой вкладке">👁️</a>',
                    f"file://{obj.file_path}",
                )
            )

        # Кнопка обновления информации
        buttons.append(
            format_html(
                '<a href="{}" class="btn btn-sm btn-primary mr-1" '
                'title="Обновить информацию">🔄</a>',
                reverse("admin:main_managedfile_refresh", args=[obj.pk]),
            )
        )

        # Кнопка создания резервной копии
        buttons.append(
            format_html(
                '<a href="{}" class="btn btn-sm btn-warning mr-1" '
                'title="Создать резервную копию">💾</a>',
                reverse("admin:main_managedfile_backup", args=[obj.pk]),
            )
        )

        # Кнопка очистки содержимого
        buttons.append(
            format_html(
                '<a href="{}" class="btn btn-sm btn-danger mr-1" '
                'title="Очистить содержимое" '
                "onclick=\"return confirm('Очистить содержимое файла?\\n"
                "Это действие нельзя отменить.')\">🗑️</a>",
                reverse("admin:main_managedfile_clear", args=[obj.pk]),
            )
        )

        return format_html(" ".join(buttons))

    actions_column.short_description = "Действия"

    def file_info_display(self, obj):
        """Отображение подробной информации о файле"""
        info = []

        if obj.exists:
            info.append(f"<strong>Существует:</strong> Да")
            info.append(f"<strong>Размер:</strong> {obj.human_readable_size}")
            info.append(f"<strong>MIME тип:</strong> {obj.mime_type}")

            if obj.file_permissions:
                info.append(f"<strong>Права доступа:</strong> {obj.file_permissions}")

            if obj.file_mtime:
                info.append(
                    f"<strong>Изменен:</strong> {obj.file_mtime.strftime('%d.%m.%Y %H:%M:%S')}"
                )

            info.append(f"<strong>Кодировка:</strong> {obj.encoding}")
            info.append(
                f"<strong>Тип:</strong> {'Текстовый' if obj.is_text_file else 'Бинарный'}"
            )
        else:
            info.append(
                '<strong style="color: red;">Файл отсутствует на диске!</strong>'
            )

        return format_html(
            '<div class="file-info" style="background: #f8f9fa; padding: 10px; '
            'border-radius: 5px; border-left: 4px solid #007bff;">'
            "{}"
            "</div>",
            "<br>".join(info),
        )

    file_info_display.short_description = "Информация о файле"

    def file_preview_display(self, obj):
        """Предпросмотр содержимого файла (первые 15 строк)"""
        if not obj.is_text_file or not obj.content:
            return "Предпросмотр недоступен для бинарных файлов"

        preview_lines = obj.content.split("\n")[:15]
        preview = "\n".join(preview_lines)

        html = f'<div style="background: #f5f5f5; padding: 10px; border-radius: 5px;">'
        html += f'<pre style="margin: 0; white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{preview}</pre>'

        if len(obj.content.split("\n")) > 15:
            html += '<div style="margin-top: 10px; padding: 5px; background: #e9ecef; border-radius: 3px;">'
            html += "<em>Показано 15 из {total_lines} строк</em>".format(
                total_lines=len(obj.content.split("\n"))
            )
            html += "</div>"

        html += "</div>"
        return mark_safe(html)

    file_preview_display.short_description = "Предпросмотр (первые 15 строк)"

    def backups_list_display(self, obj):
        """Отображение списка резервных копий файла"""
        backups = obj.get_backup_list()

        if not backups:
            return "Резервные копии отсутствуют"

        html = '<div style="max-height: 200px; overflow-y: auto;">'

        for i, backup in enumerate(backups, 1):
            html += f"""
            <div style="margin-bottom: 5px; padding: 8px; background: #e9ecef; 
                 border-radius: 3px; border-left: 3px solid #28a745;">
                <div><strong>{i}. {backup["name"]}</strong></div>
                <div style="font-size: 0.9em; color: #666;">
                    Размер: {backup["human_size"]} | 
                    Создан: {backup["modified"].strftime("%d.%m.%Y %H:%M")}
                </div>
            </div>
            """

        html += f'<p style="margin-top: 10px;"><em>Всего резервных копий: {len(backups)}</em></p>'
        html += "</div>"

        return mark_safe(html)

    backups_list_display.short_description = "Доступные резервные копии"

    def current_permissions(self, obj):
        """Отображение текущих прав доступа к файлу"""
        if not obj.exists:
            return "Файл не существует"

        perms = obj.file_permissions
        if perms:
            return format_html(
                '<code style="background: #f8f9fa; padding: 2px 5px; '
                'border-radius: 3px; font-size: 1.1em;">{}</code>',
                perms,
            )
        return "Не удалось определить"

    current_permissions.short_description = "Права доступа (octal)"

    def save_model(self, request, obj, form, change):
        """Сохранение модели с обновлением файла на диске"""
        if change and obj.content is not None and obj.is_text_file and obj.exists:
            # Проверяем размер файла перед сохранением
            content_size = len(obj.content.encode("utf-8"))
            if content_size > 5 * 1024 * 1024:  # 5 MB
                messages.error(
                    request,
                    f"Размер содержимого ({content_size / (1024 * 1024):.1f} МБ) "
                    f"превышает максимально допустимый (5 МБ)",
                )
                return

            # Создаем бэкап перед изменением
            if obj.auto_backup:
                backup_path, backup_msg = obj.create_backup()
                if backup_path:
                    messages.info(
                        request,
                        f"Создана резервная копия: {os.path.basename(backup_path)}",
                    )
                else:
                    messages.warning(
                        request, f"Не удалось создать резервную копию: {backup_msg}"
                    )

            # Сохраняем содержимое в файл
            try:
                with open(obj.file_path, "w", encoding=obj.encoding) as f:
                    f.write(obj.content)
                messages.success(request, "Файл успешно обновлен на диске")
            except Exception as e:
                messages.error(request, f"Ошибка сохранения файла: {str(e)}")
                return

        super().save_model(request, obj, form, change)

    def get_urls(self):
        """Добавляем кастомные URL для действий с файлами"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:file_id>/refresh/",
                self.admin_site.admin_view(self.refresh_file_view),
                name="main_managedfile_refresh",
            ),
            path(
                "<int:file_id>/backup/",
                self.admin_site.admin_view(self.backup_file_view),
                name="main_managedfile_backup",
            ),
            path(
                "<int:file_id>/clear/",
                self.admin_site.admin_view(self.clear_file_view),
                name="main_managedfile_clear",
            ),
            path(
                "<int:file_id>/delete-from-disk/",
                self.admin_site.admin_view(self.delete_file_from_disk_view),
                name="main_managedfile_delete_from_disk",
            ),
        ]
        return custom_urls + urls

    def refresh_file_view(self, request, file_id):
        """Обновление информации о файле из файловой системы"""
        obj = self.get_object(request, file_id)
        if obj:
            success, message = obj.refresh_file_info()
            if success:
                messages.success(request, message)
            else:
                messages.warning(request, message)

        return HttpResponseRedirect(
            reverse("admin:main_managedfile_change", args=[file_id])
        )

    def backup_file_view(self, request, file_id):
        """Создание резервной копии файла"""
        obj = self.get_object(request, file_id)
        if obj:
            backup_path, message = obj.create_backup()
            if backup_path:
                messages.success(request, message)
            else:
                messages.error(request, message)

        return HttpResponseRedirect(
            reverse("admin:main_managedfile_change", args=[file_id])
        )

    def clear_file_view(self, request, file_id):
        """Очистка содержимого файла"""
        obj = self.get_object(request, file_id)
        if obj:
            success, message = obj.clear_file()
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)

        return HttpResponseRedirect(
            reverse("admin:main_managedfile_change", args=[file_id])
        )

    def delete_file_from_disk_view(self, request, file_id):
        """Удаление файла с диска"""
        obj = self.get_object(request, file_id)
        if obj:
            success, message = obj.delete_file_from_disk()
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)

        return HttpResponseRedirect(
            reverse("admin:main_managedfile_change", args=[file_id])
        )

    # Действия для списка файлов
    def refresh_selected_files(self, request, queryset):
        """Обновить информацию о выбранных файлах"""
        updated = 0
        for obj in queryset:
            success, _ = obj.refresh_file_info()
            if success:
                updated += 1

        self.message_user(
            request, f"Информация обновлена для {updated} из {queryset.count()} файлов"
        )

    refresh_selected_files.short_description = "Обновить информацию о файлах"

    def create_backup_selected(self, request, queryset):
        """Создать резервные копии для выбранных файлов"""
        created = 0
        for obj in queryset:
            if obj.exists:
                backup_path, _ = obj.create_backup()
                if backup_path:
                    created += 1

        self.message_user(
            request,
            f"Резервные копии созданы для {created} из {queryset.count()} файлов",
        )

    create_backup_selected.short_description = "Создать резервные копии"

    def clear_selected_files(self, request, queryset):
        """Очистить выбранные файлы"""
        if request.POST.get("confirm"):
            cleared = 0
            for obj in queryset:
                if obj.exists:
                    success, _ = obj.clear_file()
                    if success:
                        cleared += 1

            self.message_user(
                request, f"Очищено {cleared} из {queryset.count()} файлов"
            )
            return None

        # Показываем страницу подтверждения
        from django.shortcuts import render

        return render(
            request,
            "admin/main/confirm_clear_files.html",
            {
                "files": queryset,
                "opts": self.model._meta,
                "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            },
        )

    clear_selected_files.short_description = "Очистить содержимое файлов"

    def toggle_active_selected(self, request, queryset):
        """Включить/выключить отслеживание файлов"""
        for obj in queryset:
            obj.is_active = not obj.is_active
            obj.save()

        self.message_user(request, f"Статус изменен для {queryset.count()} файлов")

    toggle_active_selected.short_description = "Переключить активность"

    def scan_logs_directory(self, request, queryset):
        """Сканировать директории на наличие лог-файлов"""
        from django.conf import settings

        # Определяем директории для сканирования
        scan_dirs = [
            settings.BASE_DIR,
            "/var/log",
            "/tmp",
        ]

        added_count = 0

        for scan_dir in scan_dirs:
            if os.path.exists(scan_dir):
                for root, dirs, files in os.walk(scan_dir):
                    for file in files:
                        if file.endswith((".log", ".txt", ".conf", ".ini", ".cfg")):
                            file_path = os.path.join(root, file)

                            # Проверяем, не добавлен ли уже файл
                            if not ManagedFile.objects.filter(
                                file_path=file_path
                            ).exists():
                                try:
                                    # Определяем категорию
                                    if file.endswith(".log"):
                                        category = "log"
                                    elif file.endswith((".conf", ".ini", ".cfg")):
                                        category = "config"
                                    else:
                                        category = "other"

                                    # Создаем запись
                                    ManagedFile.objects.create(
                                        name=file,
                                        file_path=file_path,
                                        category=category,
                                        description=f"Автоматически добавлен из {root}",
                                    )
                                    added_count += 1
                                except:
                                    pass

        self.message_user(request, f"Добавлено {added_count} новых файлов")

    scan_logs_directory.short_description = "Сканировать директории на наличие файлов"


def changelist_view(self, request, extra_context=None):
    """
    Переопределяем представление списка для добавления статистики
    """
    response = super().changelist_view(request, extra_context=extra_context)

    if hasattr(response, "context_data"):
        # Получаем статистику
        queryset = self.get_queryset(request)
        response.context_data["active_count"] = queryset.filter(is_active=True).count()
        response.context_data["exists_count"] = queryset.filter(exists=True).count()
        response.context_data["text_files_count"] = queryset.filter(
            is_text_file=True
        ).count()

    return response


# Также добавьте обработку сканирования директорий
def get_urls(self):
    """Добавляем кастомные URL для действий с файлами"""
    urls = super().get_urls()
    custom_urls = [
        path(
            "<int:file_id>/refresh/",
            self.admin_site.admin_view(self.refresh_file_view),
            name="main_managedfile_refresh",
        ),
        path(
            "<int:file_id>/backup/",
            self.admin_site.admin_view(self.backup_file_view),
            name="main_managedfile_backup",
        ),
        path(
            "<int:file_id>/clear/",
            self.admin_site.admin_view(self.clear_file_view),
            name="main_managedfile_clear",
        ),
        path(
            "<int:file_id>/delete-from-disk/",
            self.admin_site.admin_view(self.delete_file_from_disk_view),
            name="main_managedfile_delete_from_disk",
        ),
        # Новые URL
        path(
            "scan/",
            self.admin_site.admin_view(self.scan_directory_view),
            name="main_managedfile_scan_directory",
        ),
        path(
            "refresh-all/",
            self.admin_site.admin_view(self.refresh_all_files_view),
            name="main_managedfile_refresh_all",
        ),
        path(
            "backup-all/",
            self.admin_site.admin_view(self.backup_all_files_view),
            name="main_managedfile_backup_all",
        ),
        path(
            "scan-logs/",
            self.admin_site.admin_view(self.scan_logs_view),
            name="main_managedfile_scan_logs",
        ),
    ]
    return custom_urls + urls


def scan_directory_view(self, request):
    """Сканирование директории"""
    from django.conf import settings

    # Определяем директории для сканирования
    scan_dirs = [
        settings.BASE_DIR,
        "/var/log",
        "/tmp",
        "/home",
        settings.MEDIA_ROOT,
    ]

    added_count = 0

    for scan_dir in scan_dirs:
        if os.path.exists(scan_dir):
            for root, dirs, files in os.walk(scan_dir, topdown=True):
                # Пропускаем некоторые директории
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ["__pycache__", "node_modules", "venv", ".git"]
                ]

                for file in files:
                    # Проверяем расширения файлов
                    if file.endswith(
                        (
                            ".log",
                            ".txt",
                            ".conf",
                            ".ini",
                            ".cfg",
                            ".json",
                            ".yaml",
                            ".yml",
                            ".xml",
                            ".html",
                            ".css",
                            ".js",
                            ".py",
                            ".md",
                        )
                    ):
                        file_path = os.path.join(root, file)

                        # Проверяем, не добавлен ли уже файл
                        if not ManagedFile.objects.filter(file_path=file_path).exists():
                            try:
                                # Определяем категорию
                                if file.endswith(".log"):
                                    category = "log"
                                elif file.endswith((".conf", ".ini", ".cfg")):
                                    category = "config"
                                elif file.endswith((".py", ".js", ".html", ".css")):
                                    category = "template"
                                elif file.endswith((".json", ".yaml", ".yml", ".xml")):
                                    category = "config"
                                elif file.endswith(".txt"):
                                    category = "other"
                                else:
                                    category = "other"

                                # Создаем запись
                                ManagedFile.objects.create(
                                    name=file,
                                    file_path=file_path,
                                    category=category,
                                    description=f"Автоматически добавлен из {root}",
                                )
                                added_count += 1
                            except Exception as e:
                                print(f"Ошибка добавления файла {file_path}: {e}")

    self.message_user(request, f"Добавлено {added_count} новых файлов")
    return HttpResponseRedirect(reverse("admin:main_managedfile_changelist"))


def refresh_all_files_view(self, request):
    """Обновить информацию обо всех файлах"""
    queryset = self.get_queryset(request)
    updated = 0

    for obj in queryset:
        success, _ = obj.refresh_file_info()
        if success:
            updated += 1

    self.message_user(
        request, f"Информация обновлена для {updated} из {queryset.count()} файлов"
    )
    return HttpResponseRedirect(reverse("admin:main_managedfile_changelist"))


def backup_all_files_view(self, request):
    """Создать резервные копии всех файлов"""
    queryset = self.get_queryset(request)
    created = 0

    for obj in queryset:
        if obj.exists:
            backup_path, _ = obj.create_backup()
            if backup_path:
                created += 1

    self.message_user(
        request, f"Резервные копии созданы для {created} из {queryset.count()} файлов"
    )
    return HttpResponseRedirect(reverse("admin:main_managedfile_changelist"))


def scan_logs_view(self, request):
    """Сканировать только лог-файлы"""
    from django.conf import settings

    scan_dirs = [
        "/var/log",
        "/tmp",
        settings.BASE_DIR,
    ]

    added_count = 0

    for scan_dir in scan_dirs:
        if os.path.exists(scan_dir):
            for root, dirs, files in os.walk(scan_dir):
                for file in files:
                    if file.endswith(".log"):
                        file_path = os.path.join(root, file)

                        # Проверяем, не добавлен ли уже файл
                        if not ManagedFile.objects.filter(file_path=file_path).exists():
                            try:
                                ManagedFile.objects.create(
                                    name=file,
                                    file_path=file_path,
                                    category="log",
                                    description=f"Лог-файл из {root}",
                                )
                                added_count += 1
                            except:
                                pass

    self.message_user(request, f"Добавлено {added_count} новых лог-файлов")
    return HttpResponseRedirect(reverse("admin:main_managedfile_changelist"))

    class Media:
        css = {"all": ("css/admin-file-manager.css",)}
        js = ("js/admin-file-manager.js",)
