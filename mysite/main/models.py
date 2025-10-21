# models.py
# Модели базы данных для приложения main
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


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
