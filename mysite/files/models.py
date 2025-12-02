# models.py
# Модели базы данных для приложения files
# Определяет структуру данных для хранения информации о файлах

import os
import re
import hashlib
from pathlib import Path
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class FileCategory(models.Model):
    """
    Модель категории файлов.
    Позволяет группировать файлы по категориям для удобной организации.
    """

    # Название категории (например: "Документы", "Изображения", "Видео")
    name = models.CharField(
        _("Название категории"),
        max_length=100,
        unique=True,
        help_text=_("Уникальное название категории файлов"),
    )

    # Описание категории
    description = models.TextField(
        _("Описание"),
        blank=True,
        help_text=_("Подробное описание назначения категории"),
    )

    # Иконка категории (CSS класс или путь к изображению)
    icon = models.CharField(
        _("Иконка"),
        max_length=50,
        blank=True,
        default="fa-file",
        help_text=_("CSS класс иконки (например: fa-file, fa-image)"),
    )

    # Цвет категории для визуального отличия
    color = models.CharField(
        _("Цвет"),
        max_length=7,
        blank=True,
        default="#007bff",
        help_text=_("Цвет в формате HEX (например: #007bff)"),
    )

    # Порядок отображения категории
    order = models.IntegerField(
        _("Порядок"),
        default=0,
        help_text=_("Порядок отображения категории в списке"),
    )

    # Активна ли категория
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        help_text=_("Показывать ли категорию в интерфейсе"),
    )

    # Временные метки
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)

    class Meta:
        """Метаданные модели категории файлов."""

        verbose_name = _("Категория файлов")
        verbose_name_plural = _("Категории файлов")
        ordering = ["order", "name"]

    def __str__(self):
        """
        Строковое представление категории.
        Возвращает название категории.
        """
        return self.name


def get_upload_path(instance, filename):
    """
    Функция для определения пути загрузки файла.
    Создает структуру папок на основе категории и даты загрузки.

    Args:
        instance: Экземпляр модели File
        filename: Имя загружаемого файла

    Returns:
        str: Путь для сохранения файла
    """
    # Получаем категорию файла
    if instance.category:
        # Создаем slug из названия категории (заменяем пробелы на подчеркивания, убираем спецсимволы)
        category_slug = instance.category.name.lower().replace(" ", "_")
        # Убираем все символы кроме букв, цифр и подчеркиваний
        category_slug = re.sub(r'[^\w\-]', '', category_slug)
    else:
        category_slug = "uncategorized"
    
    # Формируем путь: files/категория/год/месяц/имя_файла
    date_path = timezone.now().strftime("%Y/%m")
    return f"files/{category_slug}/{date_path}/{filename}"


class File(models.Model):
    """
    Модель файла.
    Хранит информацию о загруженных файлах в системе.
    """

    # Название файла (может отличаться от оригинального имени)
    name = models.CharField(
        _("Название"),
        max_length=255,
        help_text=_("Отображаемое название файла"),
    )

    # Оригинальное имя файла при загрузке
    original_name = models.CharField(
        _("Оригинальное имя"),
        max_length=255,
        help_text=_("Имя файла при загрузке"),
    )

    # Файл (FileField хранит сам файл)
    file = models.FileField(
        _("Файл"),
        upload_to=get_upload_path,
        help_text=_("Загружаемый файл"),
    )

    # Категория файла
    category = models.ForeignKey(
        FileCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
        verbose_name=_("Категория"),
        help_text=_("Категория файла"),
    )

    # Описание файла
    description = models.TextField(
        _("Описание"),
        blank=True,
        help_text=_("Подробное описание содержимого файла"),
    )

    # Теги для поиска и фильтрации
    tags = models.CharField(
        _("Теги"),
        max_length=500,
        blank=True,
        help_text=_("Теги через запятую для поиска"),
    )

    # Размер файла в байтах
    file_size = models.BigIntegerField(
        _("Размер файла"),
        default=0,
        help_text=_("Размер файла в байтах"),
    )

    # MIME тип файла
    mime_type = models.CharField(
        _("MIME тип"),
        max_length=100,
        blank=True,
        help_text=_("MIME тип файла (например: image/jpeg, application/pdf)"),
    )

    # MD5 хеш файла для проверки целостности
    file_hash = models.CharField(
        _("MD5 хеш"),
        max_length=32,
        blank=True,
        help_text=_("MD5 хеш файла для проверки целостности"),
    )

    # Количество скачиваний
    download_count = models.PositiveIntegerField(
        _("Количество скачиваний"),
        default=0,
        help_text=_("Сколько раз файл был скачан"),
    )

    # Показывать ли файл публично
    is_public = models.BooleanField(
        _("Публичный"),
        default=False,
        help_text=_("Доступен ли файл для публичного просмотра"),
    )

    # Активен ли файл
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        help_text=_("Показывать ли файл в списке"),
    )

    # Пользователь, загрузивший файл
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
        verbose_name=_("Загрузил"),
        help_text=_("Пользователь, загрузивший файл"),
    )

    # Временные метки
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)

    class Meta:
        """Метаданные модели файла."""

        verbose_name = _("Файл")
        verbose_name_plural = _("Файлы")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["uploaded_by", "created_at"]),
            models.Index(fields=["file_hash"]),
        ]

    def __str__(self):
        """
        Строковое представление файла.
        Возвращает название файла.
        """
        return self.name

    def clean(self):
        """
        Валидация данных перед сохранением.
        Проверяет корректность данных файла.
        """
        super().clean()

        # Проверка размера файла (максимум 100 МБ)
        if self.file_size > 100 * 1024 * 1024:
            raise ValidationError(
                {"file": _("Размер файла не должен превышать 100 МБ")}
            )

    def save(self, *args, **kwargs):
        """
        Переопределяет сохранение для автоматического вычисления метаданных.
        Вычисляет размер, MIME тип и хеш файла при сохранении.
        """
        # Если файл был загружен, вычисляем метаданные
        if self.file and hasattr(self.file, "file"):
            # Вычисляем размер файла
            self.file_size = self.file.size

            # Определяем MIME тип
            import mimetypes

            mime_type, _ = mimetypes.guess_type(self.file.name)
            self.mime_type = mime_type or "application/octet-stream"

            # Вычисляем MD5 хеш
            self.file_hash = self._calculate_hash()

            # Если название не задано, используем оригинальное имя
            if not self.name:
                self.name = self.original_name or os.path.basename(self.file.name)

        super().save(*args, **kwargs)

    def _calculate_hash(self):
        """
        Вычисляет MD5 хеш файла для проверки целостности.

        Returns:
            str: MD5 хеш файла в виде строки
        """
        if not self.file:
            return ""

        try:
            hash_md5 = hashlib.md5()
            # Читаем файл по частям для экономии памяти
            for chunk in self.file.chunks():
                hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для просмотра файла.

        Returns:
            str: URL для просмотра файла
        """
        from django.urls import reverse

        return reverse("files:file_detail", kwargs={"pk": self.pk})

    def get_download_url(self):
        """
        Возвращает URL для скачивания файла.

        Returns:
            str: URL для скачивания файла
        """
        from django.urls import reverse

        return reverse("files:file_download", kwargs={"pk": self.pk})

    def increment_download_count(self):
        """
        Увеличивает счетчик скачиваний на 1.
        """
        self.download_count += 1
        self.save(update_fields=["download_count"])

    @property
    def human_readable_size(self):
        """
        Возвращает размер файла в человекочитаемом формате.

        Returns:
            str: Размер файла (например: "1.5 МБ")
        """
        size = self.file_size
        for unit in ["байт", "КБ", "МБ", "ГБ"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"

    @property
    def file_extension(self):
        """
        Возвращает расширение файла.

        Returns:
            str: Расширение файла (например: "pdf", "jpg")
        """
        return Path(self.original_name).suffix[1:].lower() if self.original_name else ""

    def delete(self, *args, **kwargs):
        """
        Переопределяет удаление для удаления файла с диска.
        """
        # Удаляем файл с диска
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)


class FileVersion(models.Model):
    """
    Модель версии файла.
    Хранит историю изменений файла (резервные копии).
    """

    # Связь с основным файлом
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Файл"),
        help_text=_("Основной файл"),
    )

    # Версия файла
    version_number = models.PositiveIntegerField(
        _("Номер версии"),
        help_text=_("Номер версии файла"),
    )

    # Файл версии
    version_file = models.FileField(
        _("Файл версии"),
        upload_to="files/versions/",
        help_text=_("Файл этой версии"),
    )

    # Комментарий к версии
    comment = models.TextField(
        _("Комментарий"),
        blank=True,
        help_text=_("Комментарий к этой версии"),
    )

    # Пользователь, создавший версию
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_versions",
        verbose_name=_("Создал"),
        help_text=_("Пользователь, создавший версию"),
    )

    # Временные метки
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        """Метаданные модели версии файла."""

        verbose_name = _("Версия файла")
        verbose_name_plural = _("Версии файлов")
        ordering = ["-version_number"]
        unique_together = [["file", "version_number"]]

    def __str__(self):
        """
        Строковое представление версии.
        Возвращает номер версии файла.
        """
        return f"{self.file.name} (версия {self.version_number})"

    def delete(self, *args, **kwargs):
        """
        Переопределяет удаление для удаления файла версии с диска.
        """
        if self.version_file:
            self.version_file.delete(save=False)
        super().delete(*args, **kwargs)

