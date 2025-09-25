from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class SiteSettings(models.Model):
    """Модель для хранения глобальных настроек сайта.

    Attributes:
        phone1 (CharField): Первый телефонный номер сайта.
        phone2 (CharField): Второй телефонный номер сайта.
        email (EmailField): Электронная почта сайта.
        logo (ImageField): Логотип сайта, загружаемый как изображение.
        logo_text (CharField): Текст, связанный с логотипом.
        slogan (CharField): Слоган, отображаемый в шапке сайта.
        motto (CKEditor5Field): Девиз сайта, редактируемый через CKEditor.
        short_description (CKEditor5Field): Краткое описание сайта.
        content (CKEditor5Field): Полное описание сайта.
        address (CharField): Адрес сайта.
        facebook (URLField): Ссылка на Facebook.
        instagram (URLField): Ссылка на Instagram.
        youtube (URLField): Ссылка на YouTube.
        rutube (URLField): Ссылка на Rutube.
        vk_video (URLField): Ссылка на видео в VK.
        telegram (URLField): Ссылка на Telegram.
        vk (URLField): Ссылка на ВКонтакте.
        ok (URLField): Ссылка на Одноклассники.
        site_closed (BooleanField): Флаг закрытия сайта.
        closure_message (TextField): Сообщение при закрытии сайта.

    Meta:
        verbose_name (str): Имя модели в единственном числе.
        verbose_name_plural (str): Имя модели во множественном числе.

    Methods:
        __str__: Возвращает строковое представление объекта.
        save(*args, **kwargs): Переопределённый метод сохранения, разрешающий только одну запись.
        load(): Классовый метод для получения или создания экземпляра настроек.
    """

    phone1 = models.CharField(_("Телефон 1"), max_length=20, blank=True)
    phone2 = models.CharField(_("Телефон 2"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), max_length=255, blank=True)
    logo = models.ImageField(_("Логотип"), upload_to="logos/", blank=True)
    logo_text = models.CharField(_("Текст логотипа"), max_length=100, blank=True)
    slogan = models.CharField(_("Слоган в шапке"), max_length=255, blank=True)
    motto = CKEditor5Field(_("Девиз сайта"), blank=True, config_name="extends")
    short_description = CKEditor5Field(
        _("Краткое описание"), blank=True, config_name="extends"
    )
    content = CKEditor5Field(_("Описание"), blank=True, config_name="extends")
    address = models.CharField(_("Адрес"), max_length=255, blank=True)
    facebook = models.URLField(_("Facebook"), blank=True)
    instagram = models.URLField(_("Instagram"), blank=True)
    youtube = models.URLField(_("Youtube"), blank=True)
    rutube = models.URLField(_("Rutube"), blank=True)
    vk_video = models.URLField(_("VK видео"), blank=True)
    telegram = models.URLField(_("Telegram"), blank=True)
    vk = models.URLField(_("VK"), blank=True)
    ok = models.URLField(_("OK"), blank=True)
    site_closed = models.BooleanField(_("Сайт закрыт"), default=False)
    closure_message = models.TextField(_("Сообщение при закрытии"), blank=True)

    class Meta:
        """Метаданные модели."""

        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        """
        Переопределённый метод сохранения.

        Разрешает создавать только одну запись настроек. Если запись уже существует,
        вызывается ошибка ValidationError.

        Args:
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные ключевые аргументы.

        Raises:
            ValidationError: Если попытаться создать вторую запись настроек.
        """
        # Разрешаем создавать только одну запись настроек
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Может существовать только одна запись настроек")
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Классовый метод для получения или создания экземпляра настроек.

        Всегда возвращает единственный экземпляр модели с первичным ключом 1.

        Returns:
            SiteSettings: Единственный экземпляр настроек.
        """
        # Метод для загрузки единственной записи настроек
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Page(models.Model):
    """Модель страницы сайта, представляющая структуру данных для пользовательских страниц.

    Атрибуты:
        title (CharField): Заголовок страницы (обязательное поле, максимум 200 символов).
        slug (SlugField): Уникальный URL-идентификатор страницы.
        content (CKEditor5Field): Содержание страницы с поддержкой расширенного редактора.
        show_in_menu (BooleanField): Флаг отображения страницы в меню сайта.
        show_on_site (BooleanField): Флаг отображения страницы на сайте.
        order (IntegerField): Позиция для сортировки страниц.
        seo_title (CharField): SEO-заголовок для оптимизации в поисковых системах.
        seo_keywords (CharField): SEO-ключевые слова.
        seo_description (CharField): SEO-описание страницы.
        created_at (DateTimeField): Дата и время создания страницы.
        updated_at (DateTimeField): Дата и время последнего обновления страницы.

    Meta:
        verbose_name (str): Человекочитаемое имя модели (единительное число).
        verbose_name_plural (str): Человекочитаемое имя модели (множественное число).
        ordering (list): Порядок сортировки записей по умолчанию.

    Методы:
        __str__: Возвращает строковое представление объекта (заголовок страницы).
    """

    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True)
    content = CKEditor5Field(_("Содержание"), blank=True, config_name="extends")
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    show_on_site = models.BooleanField(_("Показывать на сайте"), default=True)
    order = models.IntegerField(_("Порядок"), default=0)
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        """
        Конфигурация метаданных модели.
        """

        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")
        ordering = ["order", "title"]

    def __str__(self):
        """
        Возвращает строковое представление объекта - заголовок страницы.
        """
        return self.title
