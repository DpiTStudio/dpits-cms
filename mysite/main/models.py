# models.py
# Модели базы данных для приложения main
import os
import mimetypes
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from datetime import datetime
from pathlib import Path
from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html


class SingletonModel(models.Model):
    """
    Абстрактная модель для создания singleton-объектов (только одна запись).
    Гарантирует, что в базе данных будет только один экземпляр модели.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Переопределяет сохранение, разрешая только одну запись.
        Всегда устанавливает первичный ключ = 1.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Возвращает единственный экземпляр модели, создавая его при необходимости.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """
    Модель для хранения глобальных настроек сайта.
    Наследует SingletonModel для гарантии единственного экземпляра.
    """

    # Контактная информация
    phone1 = models.CharField(_("Основной телефон"), max_length=20, blank=True)
    phone2 = models.CharField(_("Дополнительный телефон"), max_length=20, blank=True)
    email = models.EmailField(_("Электронная почта"), max_length=255, blank=True)
    address = models.CharField(_("Адрес"), max_length=255, blank=True)

    # Брендинг и контент
    logo = models.ImageField(
        _("Логотип"),
        upload_to="logos/",
        blank=True,
        help_text=_("Рекомендуемый размер: 200x60 пикселей"),
    )
    logo_text = models.CharField(_("Текст логотипа"), max_length=100, blank=True)
    slogan = models.CharField(_("Слоган"), max_length=255, blank=True)
    motto = CKEditor5Field(_("Девиз сайта"), blank=True, config_name="extends")
    short_description = CKEditor5Field(
        _("Краткое описание"), blank=True, config_name="extends"
    )
    content = CKEditor5Field(_("Основной контент"), blank=True, config_name="extends")

    # Социальные сети
    facebook = models.URLField(_("Facebook"), blank=True)
    instagram = models.URLField(_("Instagram"), blank=True)
    youtube = models.URLField(_("YouTube"), blank=True)
    rutube = models.URLField(_("Rutube"), blank=True)
    vk_video = models.URLField(_("VK Видео"), blank=True)
    telegram = models.URLField(_("Telegram"), blank=True)
    vk = models.URLField(_("ВКонтакте"), blank=True)
    ok = models.URLField(_("Одноклассники"), blank=True)

    # SEO оптимизация
    seo_title = models.CharField(
        _("SEO заголовок (title)"),
        max_length=200,
        blank=True,
        help_text=_("Если не указан, используется заголовок страницы"),
    )
    seo_keywords = models.CharField(
        _("SEO ключевые слова"),
        max_length=200,
        blank=True,
        help_text=_("Ключевые слова через запятую"),
    )
    seo_description = models.CharField(
        _("SEO описание (description)"),
        max_length=255,
        blank=True,
        help_text=_("Краткое описание для поисковых систем"),
    )

    # Статус сайта
    site_closed = models.BooleanField(_("Сайт закрыт"), default=False)
    closure_message = models.TextField(
        _("Сообщение при закрытии"),
        blank=True,
        help_text=_("Сообщение, которое увидят пользователи при закрытии сайта"),
    )

    # Временные метки
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        """Метаданные модели настроек сайта."""

        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")

    def __str__(self):
        """
        Строковое представление объекта.
        Явно преобразуем перевод в строку чтобы избежать ошибки.
        """
        return str(_("Настройки сайта"))  # Явное преобразование в строку

    def clean(self):
        """
        Валидация данных перед сохранением.
        Проверяет корректность email и наличие сообщения при закрытии сайта.
        """
        super().clean()

        # Проверка наличия сообщения при закрытии сайта
        if self.site_closed and not self.closure_message:
            raise ValidationError(
                {
                    "closure_message": _(
                        "Необходимо указать сообщение при закрытии сайта, "
                        "если сайт помечен как закрытый"
                    )
                }
            )

        # Валидация email
        if self.email and "@" not in self.email:
            raise ValidationError({"email": _("Введите корректный email адрес")})


class Page(models.Model):
    """
    Модель для пользовательских страниц сайта.
    Поддерживает SEO, управление видимостью и порядком отображения.
    """

    # Основное содержимое
    title = models.CharField(_("Заголовок страницы"), max_length=200)
    slug = models.SlugField(_("URL-адрес"), unique=True, max_length=200)
    content = CKEditor5Field(_("Содержание"), config_name="extends")

    # Управление отображением
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    show_on_site = models.BooleanField(_("Показывать на сайте"), default=True)
    order = models.IntegerField(
        _("Порядок отображения"),
        default=0,
        help_text=_("Чем меньше число, тем выше в списке"),
    )

    # SEO оптимизация
    seo_title = models.CharField(
        _("SEO заголовок (title)"),
        max_length=200,
        blank=True,
        help_text=_("Если не указан, используется заголовок страницы"),
    )
    seo_keywords = models.CharField(
        _("SEO ключевые слова"),
        max_length=200,
        blank=True,
        help_text=_("Ключевые слова через запятую"),
    )
    seo_description = models.CharField(
        _("SEO описание (description)"),
        max_length=255,
        blank=True,
        help_text=_("Краткое описание для поисковых систем"),
    )

    # Временные метки
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)

    class Meta:
        """Метаданные модели страниц."""

        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")
        ordering = ["order", "title"]  # Сортировка по умолчанию

    def __str__(self):
        """Строковое представление - заголовок страницы."""
        return self.title

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL страницы.
        Используется в админке и шаблонах.
        """
        return reverse("main:page_detail", kwargs={"slug": self.slug})

    def get_previous_page(self):
        """
        Возвращает предыдущую страницу по порядку или дате создания.
        """
        try:
            prev_page = (
                Page.objects.filter(show_on_site=True, order__lt=self.order)
                .order_by("-order", "-created_at")
                .first()
            )
            if not prev_page:
                prev_page = (
                    Page.objects.filter(
                        show_on_site=True, created_at__lt=self.created_at
                    )
                    .order_by("-created_at")
                    .first()
                )
            return prev_page
        except Exception:
            return None

    def get_next_page(self):
        """
        Возвращает следующую страницу по порядку или дате создания.
        """
        try:
            next_page = (
                Page.objects.filter(show_on_site=True, order__gt=self.order)
                .order_by("order", "created_at")
                .first()
            )
            if not next_page:
                next_page = (
                    Page.objects.filter(
                        show_on_site=True, created_at__gt=self.created_at
                    )
                    .order_by("created_at")
                    .first()
                )
            return next_page
        except Exception:
            return None

    @property
    def display_title(self):
        """
        Возвращает заголовок для отображения.
        Если SEO заголовок не задан, использует обычный заголовок.
        """
        return self.seo_title or self.title

    def clean(self):
        """
        Валидация данных страницы.
        Проверяет, что slug не зарезервирован системой.
        """
        super().clean()

        # Запрет использования зарезервированных URL
        reserved_slugs = ["admin", "login", "logout", "password"]
        if self.slug in reserved_slugs:
            raise ValidationError({"slug": _("Этот URL-адрес зарезервирован системой")})


class ManagedFile(models.Model):
    """
    Модель для управления файлами через админку Django
    """

    FILE_CATEGORIES = [
        ("log", "Лог-файлы"),
        ("config", "Конфигурационные файлы"),
        ("template", "Шаблоны"),
        ("static", "Статические файлы"),
        ("media", "Медиа файлы"),
        ("database", "Базы данных"),
        ("backup", "Резервные копии"),
        ("other", "Другие файлы"),
    ]

    name = models.CharField(
        verbose_name="Имя файла", max_length=255, help_text="Отображаемое имя файла"
    )

    file_path = models.CharField(
        verbose_name="Полный путь к файлу",
        max_length=500,
        unique=True,
        help_text="Абсолютный путь к файлу в файловой системе",
    )

    category = models.CharField(
        verbose_name="Категория",
        max_length=20,
        choices=FILE_CATEGORIES,
        default="other",
    )

    description = models.TextField(
        verbose_name="Описание файла",
        blank=True,
        help_text="Краткое описание содержимого файла",
    )

    content = models.TextField(
        verbose_name="Содержимое файла",
        blank=True,
        null=True,
        help_text="Текстовое содержимое (только для текстовых файлов)",
    )

    is_text_file = models.BooleanField(
        verbose_name="Текстовый файл",
        default=True,
        help_text="Является ли файл текстовым (можно редактировать)",
    )

    encoding = models.CharField(
        verbose_name="Кодировка",
        max_length=50,
        default="utf-8",
        help_text="Кодировка файла",
    )

    is_active = models.BooleanField(
        verbose_name="Активен",
        default=True,
        help_text="Отслеживать ли изменения этого файла",
    )

    auto_backup = models.BooleanField(
        verbose_name="Авто-бэкап",
        default=True,
        help_text="Создавать резервную копию перед редактированием",
    )

    max_backups = models.PositiveIntegerField(
        verbose_name="Макс. бэкапов",
        default=5,
        help_text="Максимальное количество хранимых резервных копий",
    )

    # Автоматически заполняемые поля
    file_size = models.BigIntegerField(
        verbose_name="Размер файла (байт)", editable=False, default=0
    )

    file_mtime = models.DateTimeField(
        verbose_name="Время изменения файла", editable=False, null=True
    )

    mime_type = models.CharField(
        verbose_name="MIME тип", max_length=100, editable=False, default=""
    )

    last_checked = models.DateTimeField(
        verbose_name="Последняя проверка", auto_now=True
    )

    created_at = models.DateTimeField(
        verbose_name="Дата создания записи", auto_now_add=True
    )

    class Meta:
        verbose_name = "Управляемый файл"
        verbose_name_plural = "Управляемые файлы"
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["file_path"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def clean(self):
        """Валидация модели"""
        # Проверяем, что путь не пустой
        if not self.file_path:
            raise ValidationError("Путь к файлу обязателен")

        # Проверяем уникальность пути
        if (
            ManagedFile.objects.filter(file_path=self.file_path)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(f"Файл с таким путем уже существует в базе")

        # При создании проверяем существование файла
        if not self.pk and not os.path.exists(self.file_path):
            raise ValidationError(f"Файл не существует: {self.file_path}")

    def save(self, *args, **kwargs):
        """Переопределяем сохранение для обновления информации о файле"""
        # Обновляем информацию о файле, если он существует
        if os.path.exists(self.file_path):
            self._update_file_info()

        super().save(*args, **kwargs)

    def _update_file_info(self):
        """Обновляет информацию о файле"""
        try:
            stat_info = os.stat(self.file_path)
            self.file_size = stat_info.st_size
            self.file_mtime = timezone.datetime.fromtimestamp(
                stat_info.st_mtime, tz=timezone.get_current_timezone()
            )

            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(self.file_path)
            self.mime_type = mime_type or "application/octet-stream"

            # Определяем, текстовый ли файл
            if not hasattr(self, "is_text_file") or self.is_text_file is None:
                self._detect_if_text_file()

            # Читаем содержимое текстовых файлов
            if self.is_text_file and self.file_size < 5 * 1024 * 1024:  # 5 MB limit
                self._read_file_content()
        except Exception as e:
            self.file_size = 0
            self.content = f"[Ошибка доступа к файлу: {str(e)}]"

    def _read_file_content(self):
        """Читает содержимое файла с различными кодировками"""
        encodings_to_try = [
            self.encoding,
            "utf-8",
            "cp1251",
            "cp866",
            "iso-8859-1",
            "mac_cyrillic",
        ]

        for enc in encodings_to_try:
            try:
                with open(self.file_path, "r", encoding=enc) as f:
                    self.content = f.read()
                self.encoding = enc
                return
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue

        # Если все кодировки не подошли
        self.content = "[Бинарный файл или неизвестная кодировка]"
        self.is_text_file = False

    def _detect_if_text_file(self):
        """Определяет, является ли файл текстовым"""
        try:
            # Попытка прочитать как текст
            with open(self.file_path, "r", encoding="utf-8") as f:
                f.read(1024)
            self.is_text_file = True
        except:
            self.is_text_file = False

    def get_absolute_url(self):
        """URL для просмотра файла"""
        from django.urls import reverse

        return reverse("admin:main_managedfile_change", args=[self.pk])

    @property
    def exists(self):
        """Проверяет, существует ли файл"""
        return os.path.exists(self.file_path)

    @property
    def human_readable_size(self):
        """Человеко-читаемый размер файла"""
        size = self.file_size
        for unit in ["байт", "КБ", "МБ", "ГБ"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"

    @property
    def file_permissions(self):
        """Права доступа к файлу"""
        if not self.exists:
            return None

        try:
            import stat

            mode = os.stat(self.file_path).st_mode
            return oct(stat.S_IMODE(mode))
        except:
            return None

    def create_backup(self):
        """Создает резервную копию файла"""
        if not self.exists:
            return None, "Файл не существует"

        # Создаем директорию для бэкапов
        backup_dir = Path(settings.MEDIA_ROOT) / "file_backups" / self.category
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Генерируем имя файла бэкапа
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(self.file_path).name
        backup_name = f"{file_name}.backup_{timestamp}"
        backup_path = backup_dir / backup_name

        try:
            import shutil

            shutil.copy2(self.file_path, backup_path)

            # Удаляем старые бэкапы, если их больше максимума
            self._cleanup_old_backups(backup_dir, file_name)

            return str(backup_path), "Резервная копия создана успешно"
        except Exception as e:
            return None, f"Ошибка создания резервной копии: {str(e)}"

    def _cleanup_old_backups(self, backup_dir, base_name):
        """Удаляет старые резервные копии"""
        backups = sorted(
            backup_dir.glob(f"{base_name}.backup_*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        if len(backups) > self.max_backups:
            for backup in backups[self.max_backups :]:
                try:
                    backup.unlink()
                except:
                    pass

    def clear_file(self):
        """Очищает содержимое файла"""
        if not self.exists:
            return False, "Файл не существует"

        # Создаем бэкап перед очисткой
        if self.auto_backup:
            backup_path, backup_msg = self.create_backup()
        else:
            backup_msg = "Бэкап не создавался (отключен)"

        try:
            if self.is_text_file:
                with open(self.file_path, "w", encoding=self.encoding) as f:
                    f.write("")
            else:
                # Для бинарных файлов заполняем нулями
                with open(self.file_path, "wb") as f:
                    f.write(b"")

            # Обновляем информацию о файле
            self._update_file_info()
            self.save()

            return True, f"Файл очищен. {backup_msg}"
        except Exception as e:
            return False, f"Ошибка очистки файла: {str(e)}"

    def delete_file_from_disk(self):
        """Удаляет файл с диска"""
        if not self.exists:
            return False, "Файл уже не существует"

        try:
            os.remove(self.file_path)

            # Обновляем информацию
            self.file_size = 0
            self.content = "[Файл удален]"
            self.is_active = False
            self.save()

            return True, "Файл успешно удален"
        except Exception as e:
            return False, f"Ошибка удаления файла: {str(e)}"

    def refresh_file_info(self):
        """Обновляет информацию о файле из файловой системы"""
        if self.exists:
            self._update_file_info()
            self.save()
            return True, "Информация обновлена"
        else:
            self.file_size = 0
            self.content = "[Файл не существует]"
            self.is_active = False
            self.save()
            return False, "Файл не существует"

    def get_backup_list(self):
        """Возвращает список резервных копий"""
        backup_dir = Path(settings.MEDIA_ROOT) / "file_backups" / self.category
        file_name = Path(self.file_path).name

        backups = []
        for backup_file in backup_dir.glob(f"{file_name}.backup_*"):
            try:
                stat_info = backup_file.stat()
                backups.append(
                    {
                        "path": str(backup_file),
                        "name": backup_file.name,
                        "size": stat_info.st_size,
                        "modified": timezone.datetime.fromtimestamp(
                            stat_info.st_mtime, tz=timezone.get_current_timezone()
                        ),
                        "human_size": self._format_size(stat_info.st_size),
                    }
                )
            except:
                continue

        # Сортируем по дате изменения (новые сначала)
        backups.sort(key=lambda x: x["modified"], reverse=True)
        return backups

    def _format_size(self, size):
        """Форматирует размер файла"""
        for unit in ["байт", "КБ", "МБ", "ГБ"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"
