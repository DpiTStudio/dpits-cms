# models.py
# Модели базы данных для приложения main
import os  # Модуль для работы с операционной системой
import shutil  # Модуль для операций с файлами (копирование, перемещение)
import mimetypes  # Модуль для определения MIME-типов файлов
from django.utils.translation import gettext_lazy as _  # Функция для перевода строк
from django.urls import reverse  # Функция для построения URL
from django_ckeditor_5.fields import CKEditor5Field  # Поле редактора для контента
from datetime import datetime  # Класс для работы с датой и временем
from pathlib import Path  # Класс для работы с путями к файлам
from django.db import models  # Базовые классы моделей Django
from django.core.files.base import ContentFile  # Класс для работы с файловым содержимым
from django.utils import timezone  # Утилиты для работы с часовыми поясами
from django.conf import settings  # Настройки Django проекта
from django.core.exceptions import ValidationError  # Исключение для ошибок валидации
from django.utils.html import format_html  # Функция для безопасного форматирования HTML


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
    Модель для управления файлами через админку Django.
    Позволяет отслеживать, редактировать и создавать резервные копии файлов.
    """

    # Категории файлов
    CATEGORY_CHOICES = [
        ("log", _("Лог-файлы")),
        ("config", _("Конфигурационные")),
        ("template", _("Шаблоны")),
        ("static", _("Статические")),
        ("media", _("Медиа")),
        ("database", _("Базы данных")),
        ("backup", _("Резервные копии")),
        ("other", _("Другие")),
    ]

    # Основные поля
    name = models.CharField(_("Имя файла"), max_length=255)
    file_path = models.CharField(_("Полный путь"), max_length=500, unique=True)
    category = models.CharField(
        _("Категория"), max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    description = models.TextField(_("Описание"), blank=True)
    is_active = models.BooleanField(_("Активен"), default=True)
    is_text_file = models.BooleanField(_("Текстовый файл"), default=True)
    encoding = models.CharField(_("Кодировка"), max_length=50, default="utf-8")
    auto_backup = models.BooleanField(_("Авто-бэкап"), default=True)
    max_backups = models.IntegerField(_("Макс. бэкапов"), default=5)

    # Информация о файле
    file_size = models.BigIntegerField(_("Размер файла"), default=0)
    file_mtime = models.DateTimeField(_("Время изменения"), null=True, blank=True)
    mime_type = models.CharField(_("MIME тип"), max_length=100, blank=True)
    file_permissions = models.CharField(_("Права доступа"), max_length=10, blank=True)

    # Содержимое файла (только для текстовых файлов)
    content = models.TextField(_("Содержимое"), blank=True, null=True)

    # Системные поля
    last_checked = models.DateTimeField(_("Последняя проверка"), auto_now=True)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)

    class Meta:
        verbose_name = _("Управляемый файл")
        verbose_name_plural = _("Управляемые файлы")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def exists(self):
        """Проверяет, существует ли файл на диске."""
        return os.path.exists(self.file_path) if self.file_path else False

    @property
    def human_readable_size(self):
        """Возвращает размер файла в удобочитаемом формате."""
        if not self.file_size:
            return "0 B"

        size = float(self.file_size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def get_category_display(self):
        """Возвращает отображаемое имя категории."""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    def refresh_file_info(self):
        """Обновляет информацию о файле с диска."""
        try:
            if not self.file_path or not os.path.exists(self.file_path):
                return False, "Файл не существует"

            # Получаем информацию о файле
            stat_info = os.stat(self.file_path)
            self.file_size = stat_info.st_size
            self.file_mtime = timezone.make_aware(
                datetime.fromtimestamp(stat_info.st_mtime)
            )

            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(self.file_path)
            self.mime_type = mime_type or "application/octet-stream"

            # Определяем права доступа
            self.file_permissions = oct(stat_info.st_mode)[-3:]

            # Проверяем, текстовый ли файл
            self.is_text_file = self._check_if_text_file()

            # Загружаем содержимое для текстовых файлов
            if self.is_text_file and self.file_size < 5 * 1024 * 1024:  # 5 MB limit
                try:
                    with open(
                        self.file_path, "r", encoding=self.encoding, errors="replace"
                    ) as f:
                        self.content = f.read()
                except (UnicodeDecodeError, IOError):
                    self.is_text_file = False
                    self.content = None
            else:
                self.content = None

            self.save()
            return True, "Информация обновлена"

        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def _check_if_text_file(self):
        """Проверяет, является ли файл текстовым."""
        if not self.exists:
            return False

        try:
            # Проверяем первые 1024 байта на наличие бинарных данных
            with open(self.file_path, "rb") as f:
                chunk = f.read(1024)

            # Если файл пустой, считаем его текстовым
            if not chunk:
                return True

            # Проверяем наличие нулевых байтов (признак бинарного файла)
            if b"\x00" in chunk:
                return False

            # Пытаемся декодировать как текст
            try:
                chunk.decode("utf-8", errors="strict")
                return True
            except UnicodeDecodeError:
                return False

        except Exception:
            return False

    def clear_file(self):
        """Очищает содержимое файла."""
        try:
            if not self.exists:
                return False, "Файл не существует"

            # Создаем бэкап перед очисткой
            if self.auto_backup:
                self.create_backup()

            # Очищаем файл
            with open(self.file_path, "w", encoding=self.encoding) as f:
                f.write("")

            # Обновляем информацию
            self.refresh_file_info()
            return True, "Файл очищен"

        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def create_backup(self):
        """Создает резервную копию файла."""
        try:
            if not self.exists:
                return None, "Файл не существует"

            # Создаем директорию для бэкапов
            backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)

            # Генерируем имя файла для бэкапа
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(self.file_path)}.backup_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)

            # Копируем файл
            shutil.copy2(self.file_path, backup_path)

            # Очищаем старые бэкапы
            self.cleanup_old_backups(backup_dir)

            return backup_path, "Резервная копия создана"

        except Exception as e:
            return None, f"Ошибка создания бэкапа: {str(e)}"

    def cleanup_old_backups(self, backup_dir):
        """Очищает старые бэкапы."""
        try:
            if not os.path.exists(backup_dir):
                return

            base_name = os.path.basename(self.file_path)
            backup_pattern = os.path.join(backup_dir, f"{base_name}.backup_*")

            import glob

            backups = sorted(glob.glob(backup_pattern), key=os.path.getmtime)

            # Удаляем старые бэкапы, если превышен лимит
            while len(backups) > self.max_backups:
                oldest_backup = backups.pop(0)
                try:
                    os.remove(oldest_backup)
                except Exception:
                    pass

        except Exception as e:
            print(f"Ошибка очистки бэкапов: {e}")

    def get_backup_list(self):
        """Возвращает список резервных копий."""
        backups = []
        try:
            backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
            if os.path.exists(backup_dir):
                import glob

                base_name = os.path.basename(self.file_path)
                backup_pattern = os.path.join(backup_dir, f"{base_name}.backup_*")

                for backup_path in sorted(
                    glob.glob(backup_pattern), key=os.path.getmtime, reverse=True
                ):
                    try:
                        stat_info = os.stat(backup_path)
                        backups.append(
                            {
                                "path": backup_path,
                                "name": os.path.basename(backup_path),
                                "size": stat_info.st_size,
                                "human_size": self._format_size(stat_info.st_size),
                                "modified": timezone.make_aware(
                                    datetime.fromtimestamp(stat_info.st_mtime)
                                ),
                            }
                        )
                    except Exception:
                        continue
        except Exception as e:
            print(f"Ошибка получения списка бэкапов: {e}")

        return backups

    def _format_size(self, size):
        """Форматирует размер файла."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def delete_file_from_disk(self):
        """Удаляет файл с диска."""
        try:
            if not self.exists:
                return False, "Файл не существует"

            # Создаем бэкап перед удалением
            if self.auto_backup:
                self.create_backup()

            # Удаляем файл
            os.remove(self.file_path)

            # Обновляем информацию
            self.file_size = 0
            self.file_mtime = None
            self.mime_type = ""
            self.file_permissions = ""
            self.content = None
            self.save()

            return True, "Файл удален с диска"

        except Exception as e:
            return False, f"Ошибка удаления файла: {str(e)}"

    @classmethod
    def get_existing_files(cls):
        """
        Возвращает QuerySet файлов, которые существуют на диске.
        Используется для фильтрации в админке.
        """
        from django.db.models import Q, Case, When, Value, BooleanField

        # Более сложный способ: возвращаем все файлы с аннотацией
        return cls.objects.all().annotate(
            exists_on_disk=Case(
                *[
                    When(file_path__isnull=True, then=Value(False)),
                    When(file_path__exact="", then=Value(False)),
                ],
                default=Value(True),
                output_field=BooleanField(),
            )
        )

    def get_files_exists_count(self):
        """
        Подсчитывает количество файлов, которые существуют на диске.
        """
        count = 0
        for obj in ManagedFile.objects.all():
            if obj.exists:
                count += 1
        return count
