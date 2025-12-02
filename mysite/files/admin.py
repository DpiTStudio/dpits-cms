# admin.py
# Админ-панель для приложения files
# Настраивает интерфейс администратора для управления файлами

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import File, FileCategory, FileVersion


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    """
    Админ-панель для категорий файлов.
    Позволяет управлять категориями файлов через интерфейс администратора.
    """

    # Поля для отображения в списке
    list_display = [
        "name",
        "icon_display",
        "color_display",
        "order",
        "file_count",
        "is_active",
        "created_at",
    ]

    # Фильтры в правой панели
    list_filter = ["is_active", "created_at"]

    # Поля для поиска
    search_fields = ["name", "description"]

    # Редактируемые поля прямо в списке
    list_editable = ["order", "is_active"]

    # Поля только для чтения
    readonly_fields = ["created_at", "updated_at"]

    # Группировка полей по секциям
    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": ("name", "description", "icon", "color", "order", "is_active"),
            },
        ),
        (
            _("Метаданные"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
    )

    def icon_display(self, obj):
        """
        Отображает иконку категории.

        Args:
            obj: Экземпляр FileCategory

        Returns:
            str: HTML с иконкой
        """
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return "—"

    icon_display.short_description = _("Иконка")

    def color_display(self, obj):
        """
        Отображает цвет категории.

        Args:
            obj: Экземпляр FileCategory

        Returns:
            str: HTML с цветным квадратом
        """
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; '
                'background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
                obj.color,
                obj.color,
            )
        return "—"

    color_display.short_description = _("Цвет")

    def file_count(self, obj):
        """
        Показывает количество файлов в категории.

        Args:
            obj: Экземпляр FileCategory

        Returns:
            int: Количество файлов
        """
        return obj.files.count()

    file_count.short_description = _("Количество файлов")


class FileVersionInline(admin.TabularInline):
    """
    Встроенная админ-панель для версий файла.
    Позволяет управлять версиями файла прямо на странице редактирования файла.
    """

    model = FileVersion
    extra = 0  # Не показывать пустые формы
    readonly_fields = ["version_number", "created_at", "created_by"]
    fields = ["version_number", "version_file", "comment", "created_by", "created_at"]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """
    Админ-панель для файлов.
    Позволяет управлять файлами через интерфейс администратора.
    """

    # Поля для отображения в списке
    list_display = [
        "name",
        "category",
        "file_size_display",
        "mime_type",
        "download_count",
        "is_public",
        "is_active",
        "uploaded_by",
        "created_at",
    ]

    # Фильтры в правой панели
    list_filter = [
        "category",
        "is_public",
        "is_active",
        "created_at",
        "uploaded_by",
    ]

    # Поля для поиска
    search_fields = ["name", "original_name", "description", "tags"]

    # Редактируемые поля прямо в списке
    list_editable = ["is_public", "is_active"]

    # Поля только для чтения
    readonly_fields = [
        "file_size",
        "mime_type",
        "file_hash",
        "download_count",
        "created_at",
        "updated_at",
        "file_preview",
    ]

    # Группировка полей по секциям
    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": (
                    "name",
                    "original_name",
                    "file",
                    "category",
                    "description",
                    "tags",
                ),
            },
        ),
        (
            _("Настройки доступа"),
            {
                "fields": ("is_public", "is_active", "uploaded_by"),
            },
        ),
        (
            _("Метаданные файла"),
            {
                "fields": (
                    "file_size",
                    "mime_type",
                    "file_hash",
                    "download_count",
                ),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
        (
            _("Предпросмотр"),
            {
                "fields": ("file_preview",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Временные метки"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # Встроенная админ-панель для версий
    inlines = [FileVersionInline]

    def file_size_display(self, obj):
        """
        Отображает размер файла в человекочитаемом формате.

        Args:
            obj: Экземпляр File

        Returns:
            str: Размер файла (например: "1.5 МБ")
        """
        return obj.human_readable_size

    file_size_display.short_description = _("Размер")

    def file_preview(self, obj):
        """
        Показывает предпросмотр файла (для изображений).

        Args:
            obj: Экземпляр File

        Returns:
            str: HTML с предпросмотром
        """
        if obj.file and obj.mime_type and obj.mime_type.startswith("image/"):
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.file.url,
            )
        return _("Предпросмотр недоступен (не изображение)")

    file_preview.short_description = _("Предпросмотр")

    def get_queryset(self, request):
        """
        Оптимизирует запросы к базе данных.

        Args:
            request: HTTP-запрос

        Returns:
            QuerySet: Оптимизированный queryset
        """
        qs = super().get_queryset(request)
        return qs.select_related("category", "uploaded_by").prefetch_related("versions")


@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    """
    Админ-панель для версий файлов.
    Позволяет управлять версиями файлов через интерфейс администратора.
    """

    # Поля для отображения в списке
    list_display = [
        "file",
        "version_number",
        "created_by",
        "created_at",
        "file_size_display",
    ]

    # Фильтры в правой панели
    list_filter = ["created_at", "file"]

    # Поля для поиска
    search_fields = ["file__name", "comment"]

    # Поля только для чтения
    readonly_fields = ["created_at", "created_by"]

    # Группировка полей по секциям
    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": ("file", "version_number", "version_file", "comment"),
            },
        ),
        (
            _("Метаданные"),
            {
                "fields": ("created_by", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def file_size_display(self, obj):
        """
        Отображает размер файла версии в человекочитаемом формате.

        Args:
            obj: Экземпляр FileVersion

        Returns:
            str: Размер файла (например: "1.5 МБ")
        """
        if obj.version_file:
            size = obj.version_file.size
            for unit in ["байт", "КБ", "МБ", "ГБ"]:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} ТБ"
        return "—"

    file_size_display.short_description = _("Размер")

    def save_model(self, request, obj, form, change):
        """
        Переопределяет сохранение для автоматического заполнения created_by.

        Args:
            request: HTTP-запрос
            obj: Экземпляр FileVersion
            form: Форма
            change: Флаг изменения существующего объекта
        """
        if not change:  # При создании нового объекта
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

