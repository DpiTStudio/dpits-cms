# models.py
"""
МОДЕЛИ БАЗЫ ДАННЫХ ДЛЯ ПРИЛОЖЕНИЯ MAIN

Этот файл содержит все модели (таблицы базы данных) для основного приложения.
Модели определяют структуру данных и бизнес-логику приложения.

Содержит:
- SingletonModel: Базовая модель для объектов-одиночек (только один экземпляр)
- SiteSettings: Глобальные настройки сайта (контакты, лого, SEO и т.д.)
- Page: Пользовательские страницы сайта с поддержкой CMS
- ManagedFile: Управление файлами на диске через админ-панель
- LogStats: Статистика лог-файлов для мониторинга системы

Каждая модель включает поля, методы валидации, свойства и бизнес-логику.
Используются дополнительные библиотеки: django-ckeditor-5 для редактирования контента.
"""

import os  # Модуль для работы с операционной системой (файлы, директории)
import shutil  # Модуль для операций с файлами (копирование, перемещение)
import mimetypes  # Модуль для определения MIME-типов файлов (текстовый/бинарный)
from django.core.files.storage import default_storage
from django.utils.text import slugify, get_valid_filename
from django.utils.translation import (
    gettext_lazy as _,
)  # Функция для интернационализации строк
from django.urls import reverse  # Функция для построения абсолютных URL
from django_ckeditor_5.fields import (
    CKEditor5Field,
)  # Поле WYSIWYG редактора для контента
from datetime import datetime  # Класс для работы с датой и временем
from django.db import models  # Базовые классы моделей Django ORM
from django.utils import timezone  # Утилиты для работы с часовыми поясами
from django.core.exceptions import ValidationError  # Исключение для ошибок валидации

# Функции для загрузки файлов с переименованием
def upload_to_with_date(instance, filename, prefix=None):
    """
    Генерирует путь для загрузки файла с переименованием в формате:
    upload_to/prefix_YYYY-MM-DD_HH-MM-SS.ext
    """
    # Если префикс не указан, пытаемся определить его
    if not prefix:
        if isinstance(instance, SiteSettings):
            prefix = "site"
        elif isinstance(instance, Page):
            prefix = "page"
        else:
            prefix = "file"

    # Определяем папку загрузки на основе модели
    upload_to = "uploads/"
    if isinstance(instance, SiteSettings):
        if "logo" in filename.lower():
            upload_to = "logos/"
        elif "hero" in filename.lower():
            upload_to = "hero_bg/"
        elif "icon" in filename.lower():
            upload_to = "icons/social/"
    elif isinstance(instance, Page):
        upload_to = "pages/"

    # Получаем текущую дату и время
    now = timezone.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Получаем расширение файла
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    # Генерируем новое имя файла
    new_filename = f"{prefix}_{date_str}{ext}"
    
    # Возвращаем полный путь
    return os.path.join(upload_to, new_filename)

# Функции-заглушки для загрузки файлов (для поддержки миграций)
def upload_to_logos(instance, filename): 
    """
    Загрузка логотипа
    """
    return upload_to_with_date(instance, filename, "logo")
def upload_to_hero_bg(instance, filename): 
    """
    Загрузка фона Hero-секции
    """
    return upload_to_with_date(instance, filename, "hero_bg")
def upload_to_facebook_icon(instance, filename): 
    """
    Загрузка иконки Facebook
    """
    return upload_to_with_date(instance, filename, "facebook_icon")
def upload_to_instagram_icon(instance, filename): 
    """
    Загрузка иконки Instagram
    """
    return upload_to_with_date(instance, filename, "instagram_icon")
def upload_to_youtube_icon(instance, filename): 
    """
    Загрузка иконки YouTube
    """
    return upload_to_with_date(instance, filename, "youtube_icon")
def upload_to_rutube_icon(instance, filename): 
    """
    Загрузка иконки Rutube
    """
    return upload_to_with_date(instance, filename, "rutube_icon")
def upload_to_vk_video_icon(instance, filename): 
    """
    Загрузка иконки VK Видео
    """
    return upload_to_with_date(instance, filename, "vk_video_icon")
def upload_to_telegram_icon(instance, filename): 
    """
    Загрузка иконки Telegram
    """
    return upload_to_with_date(instance, filename, "telegram_icon")
def upload_to_vk_icon(instance, filename): 
    """
    Загрузка иконки VK
    """
    return upload_to_with_date(instance, filename, "vk_icon")
def upload_to_ok_icon(instance, filename): 
    """
    Загрузка иконки OK
    """
    return upload_to_with_date(instance, filename, "ok_icon")
def upload_to_twitter_icon(instance, filename): 
    """
    Загрузка иконки Twitter
    """
    return upload_to_with_date(instance, filename, "twitter_icon")
def upload_to_pinterest_icon(instance, filename): 
    """
    Загрузка иконки Pinterest
    """
    return upload_to_with_date(instance, filename, "pinterest_icon")
def upload_to_linkedin_icon(instance, filename): 
    """
    Загрузка иконки LinkedIn
    """
    return upload_to_with_date(instance, filename, "linkedin_icon")
def upload_to_whatsapp_icon(instance, filename): 
    """
    Загрузка иконки WhatsApp
    """
    return upload_to_with_date(instance, filename, "whatsapp_icon")
def upload_to_viber_icon(instance, filename): 
    """
    Загрузка иконки Viber
    """
    return upload_to_with_date(instance, filename, "viber_icon")
def upload_to_skype_icon(instance, filename): 
    """
    Загрузка иконки Skype
    """
    return upload_to_with_date(instance, filename, "skype_icon")
def upload_to_threads_icon(instance, filename): 
    """
    Загрузка иконки Threads
    """
    return upload_to_with_date(instance, filename, "threads_icon")


# Модели для хранения настроек сайта
class SingletonModel(models.Model):
    """
    Абстрактная модель для создания singleton-объектов (только одна запись).
    Гарантирует, что в базе данных будет только один экземпляр модели.
    Используется для настроек сайта и других глобальных конфигураций.
    """

    class Meta:
        abstract = True  # Указывает, что это абстрактный класс (не создает таблицу)

    def save(self, *args, **kwargs):
        """
        Сохраняет объект, гарантируя что есть только одна запись.

        Действия:
        1. Принудительно устанавливает первичный ключ = 1
        2. Вызывает родительский метод save()
        3. Гарантирует, что в базе будет только одна запись
        """
        self.pk = 1  # Всегда устанавливаем ID = 1
        super().save(*args, **kwargs)  # Вызываем стандартное сохранение Django

    @classmethod
    def load(cls):
        """
        Загружает единственный экземпляр модели, создавая его при необходимости.

        Возвращает:
            obj: Единственный экземпляр модели
        """
        obj, created = cls.objects.get_or_create(
            pk=1
        )  # Получаем или создаем запись с ID=1
        return obj  # Возвращаем объект


# Миксины для добавления настроек Hero-секции в любую модель
class HeroMixin(models.Model):
    """
    Абстрактный класс (миксин) для добавления настроек Hero-секции в любую модель.
    Позволяет индивидуально настраивать заголовок, подзаголовок и фон для каждой страницы или категории.
    """

    hero_title = models.CharField(
        _("Заголовок Hero"),
        max_length=255,
        blank=True,
        help_text=_("Если не заполнено, будет использовано стандартное название"),
    )
    hero_subtitle = models.TextField(
        _("Подзаголовок Hero"),
        blank=True,
        help_text=_("Если не заполнено, будет использовано краткое описание"),
    )
    hero_image = models.ImageField(
        _("Фон Hero"),
        upload_to="hero_overrides/",
        blank=True,
        help_text=_("Переопределяет фоновое изображение для этой конкретной страницы"),
    )
    hero_is_active = models.BooleanField(
        _("Показывать Hero"),
        default=True,
        help_text=_("Снимите галочку, чтобы скрыть Hero-секцию на этой странице"),
    )

    class Meta:
        abstract = True


# Модель для хранения настроек Hero-секции для основных разделов сайта
class AppHeroSettings(HeroMixin):
    """
    Модель для настройки Hero-секций основных разделов сайта (списков новостей, услуг и т.д.).
    Используется там, где нет привязки к конкретному объекту из базы данных.
    """

    APP_CHOICES = [
        ("news", _("Новости (общий список)")),
        ("portfolio", _("Портфолио (общий список)")),
        ("services", _("Услуги (общий список)")),
        ("reviews", _("Отзывы")),
        ("contacts", _("Контакты")),
        ("about", _("О нас")),
        ("profile", _("Профиль")),
        ("home", _("Главная страница")),
    ]
    app_name = models.CharField(
        _("Раздел сайта"), max_length=50, choices=APP_CHOICES, unique=True
    )

    class Meta:
        verbose_name = _("Hero раздел")
        verbose_name_plural = _("Hero разделы")

    def __str__(self):
        return self.get_app_name_display()


# Модель для хранения глобальных настроек сайта
class SiteSettings(SingletonModel):
    """
    Модель для хранения глобальных настроек сайта.
    Наследует SingletonModel для гарантии единственного экземпляра.
    Содержит контакты, логотип, SEO-настройки и статус сайта.
    """

    # Брендинг и контент
    logo = models.ImageField(
        _("Логотип"),
        upload_to=upload_to_logos,
        blank=True,
        help_text=_("Рекомендуемый размер: 200x60 пикселей"),
    )
    
    company_name = models.CharField(
        _("Название компании"), 
        max_length=100, 
        default="",
        help_text=_("Название компании для отображения в заголовках страниц")
    )

    hero_background = models.ImageField(
        _("Фон Hero-секции"),
        upload_to=upload_to_hero_bg,
        blank=True,
        help_text=_("Изображение для фонового баннера на главной странице"),
    )

    # Социальные сети
    facebook = models.URLField(_("Facebook"), blank=True)
    icon_facebook = models.ImageField(
        _("Иконка Facebook"),
        upload_to=upload_to_facebook_icon,
        help_text=_("Иконка для соцсети Facebook"),
        blank=True
    )
    
    instagram = models.URLField(_("Instagram"), blank=True)
    icon_instagram = models.ImageField(
        _("Иконка Instagram"),
        upload_to=upload_to_instagram_icon,
        help_text=_("Иконка для соцсети Instagram"),
        blank=True
    )
    
    youtube = models.URLField(_("YouTube"), blank=True)
    icon_youtube = models.ImageField(
        _("Иконка YouTube"),
        upload_to=upload_to_youtube_icon,
        help_text=_("Иконка для соцсети YouTube"),
        blank=True
    )

    rutube = models.URLField(_("Rutube"), blank=True)
    icon_rutube = models.ImageField(
        _("Иконка Rutube"),
        upload_to=upload_to_rutube_icon,
        help_text=_("Иконка для соцсети Rutube"),
        blank=True
    )

    vk_video = models.URLField(_("VK Видео"), blank=True)
    icon_vk_video = models.ImageField(
        _("Иконка VK Видео"),
        upload_to=upload_to_vk_video_icon,
        help_text=_("Иконка для соцсети VK Видео"),
        blank=True
    )

    telegram = models.URLField(_("Telegram"), blank=True)
    icon_telegram = models.ImageField(
        _("Иконка Telegram"),
        upload_to=upload_to_telegram_icon,
        help_text=_("Иконка для соцсети Telegram"),
        blank=True
    )

    vk = models.URLField(_("ВКонтакте"), blank=True)
    icon_vk = models.ImageField(
        _("Иконка ВКонтакте"),
        upload_to=upload_to_vk_icon,
        help_text=_("Иконка для соцсети ВКонтакте"),
        blank=True
    )

    ok = models.URLField(_("Одноклассники"), blank=True)
    icon_ok = models.ImageField(
        _("Иконка Одноклассники"),
        upload_to=upload_to_ok_icon,
        help_text=_("Иконка для соцсети Одноклассники"),
        blank=True
    )

    # Новые поля для соцсетей и мессенджеров
    twitter = models.URLField(_("Twitter (X)"), blank=True)
    icon_twitter = models.ImageField(
        _("Иконка Twitter (X)"),
        upload_to=upload_to_twitter_icon,
        help_text=_("Иконка для соцсети Twitter (X)"),
        blank=True
    )
    pinterest = models.URLField(_("Pinterest"), blank=True)
    icon_pinterest = models.ImageField(
        _("Иконка Pinterest"),
        upload_to=upload_to_pinterest_icon,
        help_text=_("Иконка для соцсети Pinterest"),
        blank=True
    )
    linkedin = models.URLField(_("LinkedIn"), blank=True)
    icon_linkedin = models.ImageField(
        _("Иконка LinkedIn"),
        upload_to=upload_to_linkedin_icon,
        help_text=_("Иконка для соцсети LinkedIn"),
        blank=True
    )
    whatsapp = models.CharField(_("WhatsApp"), max_length=100, blank=True, help_text=_("Номер телефона или ссылка"))
    icon_whatsapp = models.ImageField(
        _("Иконка WhatsApp"),
        upload_to=upload_to_whatsapp_icon,
        help_text=_("Иконка для соцсети WhatsApp"),
        blank=True
    )
    viber = models.CharField(_("Viber"), max_length=100, blank=True, help_text=_("Номер телефона или ссылка"))
    icon_viber = models.ImageField(
        _("Иконка Viber"),
        upload_to=upload_to_viber_icon,
        help_text=_("Иконка для соцсети Viber"),
        blank=True
    )
    skype = models.CharField(_("Skype"), max_length=100, blank=True, help_text=_("Логин или ссылка"))
    icon_skype = models.ImageField(
        _("Иконка Skype"),
        upload_to=upload_to_skype_icon,
        help_text=_("Иконка для соцсети Skype"),
        blank=True
    )
    threads = models.URLField(_("Threads"), blank=True)
    icon_threads = models.ImageField(
        _("Иконка Threads"),
        upload_to=upload_to_threads_icon,
        help_text=_("Иконка для соцсети Threads"),
        blank=True
    )

    # Контактная информация
    title = models.CharField(_("Название сайта"), max_length=100, blank=True)
    phone1 = models.CharField(_("Основной телефон"), max_length=20, blank=True)
    phone2 = models.CharField(_("Дополнительный телефон"), max_length=20, blank=True)
    email = models.EmailField(_("Электронная почта"), max_length=255, blank=True)
    address = models.CharField(_("Адрес"), max_length=255, blank=True)
    
    # Текстовые поля
    domain = models.CharField(_("Домен"), max_length=100, blank=True, default="dpits-cms.ru")
    slogan_domain = models.CharField(_("Слоган домена"), max_length=255, blank=True, default="Разработка сайтов и веб-приложений")
    logo_text = models.CharField(_("Текст логотипа"), max_length=100, blank=True)
    slogan = models.CharField(_("Слоган"), max_length=255, blank=True)
    motto = CKEditor5Field(_("Девиз сайта"), blank=True, config_name="extends")
    short_description = CKEditor5Field(
        _("Краткое описание"), blank=True, config_name="extends"
    )
    content = CKEditor5Field(_("Основной контент"), blank=True, config_name="extends")
    
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
        return str(_("Настройки сайта"))

    def get_social_links(self):
        """
        Возвращает словарь активных ссылок на социальные сети.
        Удобно для итерации в шаблонах.
        """
        links = []
        social_fields = [
            ('facebook', 'icon_facebook', 'Facebook'),
            ('instagram', 'icon_instagram', 'Instagram'),
            ('youtube', 'icon_youtube', 'YouTube'),
            ('rutube', 'icon_rutube', 'Rutube'),
            ('vk_video', 'icon_vk_video', 'VK Видео'),
            ('telegram', 'icon_telegram', 'Telegram'),
            ('vk', 'icon_vk', 'ВКонтакте'),
            ('ok', 'icon_ok', 'Одноклассники'),
            ('twitter', None, 'Twitter'),
            ('pinterest', None, 'Pinterest'),
            ('linkedin', None, 'LinkedIn'),
            ('threads', None, 'Threads'),
        ]
        
        for field, icon_field, name in social_fields:
            val = getattr(self, field)
            if val:
                icon = None
                if icon_field:
                    icon_obj = getattr(self, icon_field)
                    icon = icon_obj.url if icon_obj else None
                links.append({
                    'name': name,
                    'url': val,
                    'icon': icon,
                    'slug': field
                })
        
        # Обработка мессенджеров
        messengers = [
            ('whatsapp', 'WhatsApp', 'https://wa.me/'),
            ('viber', 'Viber', 'viber://chat?number='),
            ('skype', 'Skype', 'skype:'),
        ]
        for field, name, base_url in messengers:
            val = getattr(self, field)
            if val:
                url = val if val.startswith(('http', 'viber:', 'skype:')) else f"{base_url}{val}"
                links.append({
                    'name': name,
                    'url': url,
                    'icon': None,
                    'slug': field
                })
                
        return links

    def clean(self):
        """
        Валидация данных перед сохранением.
        """
        super().clean()

        if self.site_closed and not self.closure_message:
            raise ValidationError({
                "closure_message": _(
                    "Необходимо указать сообщение при закрытии сайта, "
                    "если сайт помечен как закрытый"
                )
            })

        if self.email and "@" not in self.email:
            raise ValidationError({"email": _("Введите корректный email адрес")})


# Модель для пользовательских страниц сайта
class Page(HeroMixin):
    """
    Модель для пользовательских страниц сайта.
    Поддерживает SEO, управление видимостью и порядком отображения.
    Используется для CMS функциональности.
    """

    # Основное содержимое
    title = models.CharField(_("Заголовок страницы"), max_length=200)
    # Заголовок страницы, отображается пользователям

    slug = models.SlugField(_("URL-адрес"), unique=True, max_length=200)
    # Человекочитаемая часть URL (например, "o-nas"), должна быть уникальной

    content = CKEditor5Field(_("Содержание"), config_name="extends")
    # Основное содержимое страницы с поддержкой WYSIWYG редактора

    # Управление отображением
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    # Флаг, указывающий показывать ли страницу в навигационном меню

    show_on_site = models.BooleanField(_("Показывать на сайте"), default=True)
    # Флаг, указывающий активна ли страница на сайте

    order = models.IntegerField(
        _("Порядок отображения"),
        default=0,
        help_text=_("Чем меньше число, тем выше в списке"),
    )
    # Число для сортировки страниц (меньшее значение = выше в списке)

    # SEO оптимизация
    seo_title = models.CharField(
        _("SEO заголовок (title)"),
        max_length=200,
        blank=True,
        help_text=_("Если не указан, используется заголовок страницы"),
    )
    # SEO-оптимизированный заголовок (для поисковых систем)

    seo_keywords = models.CharField(
        _("SEO ключевые слова"),
        max_length=200,
        blank=True,
        help_text=_("Ключевые слова через запятую"),
    )
    # Ключевые слова для поисковых систем

    seo_description = models.CharField(
        _("SEO описание (description)"),
        max_length=255,
        blank=True,
        help_text=_("Краткое описание для поисковых систем"),
    )
    # Мета-описание для поисковых систем

    # Временные метки
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    # Дата и время создания страницы

    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)
    # Дата и время последнего обновления страницы

    class Meta:
        """Метаданные модели страниц."""

        verbose_name = _("Страница")  # Имя в единственном числе
        verbose_name_plural = _("Страницы")  # Имя во множественном числе
        ordering = ["order", "title"]  # Порядок сортировки по умолчанию

    def __str__(self):
        """
        Возвращает строковое представление страницы.

        Возвращает:
            str: Заголовок страницы
        """
        return self.title

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL страницы.
        Используется в админке и шаблонах для создания ссылок.

        Возвращает:
            str: Абсолютный URL вида /page/slug/
        """
        return reverse("main:page_detail", kwargs={"slug": self.slug})
        # Генерирует URL используя имя маршрута и параметр slug

    def get_previous_page(self):
        """
        Возвращает предыдущую страницу по порядку или дате создания.

        Логика поиска:
        1. Ищем страницы с меньшим значением order
        2. Если не найдено, ищем по более ранней дате создания
        3. Возвращает первую найденную или None

        Возвращает:
            Page или None: Предыдущая страница или None если не найдена
        """
        try:
            # Пытаемся найти по порядку (основной критерий)
            prev_page = (
                Page.objects.filter(show_on_site=True, order__lt=self.order)
                .order_by("-order", "-created_at")  # Сортируем по убыванию order и даты
                .first()  # Берем первую запись
            )

            if not prev_page:
                # Если не нашли по order, ищем по дате создания
                prev_page = (
                    Page.objects.filter(
                        show_on_site=True, created_at__lt=self.created_at
                    )
                    .order_by("-created_at")  # Сортируем по убыванию даты
                    .first()
                )
            return prev_page
        except Exception:
            # В случае ошибки возвращаем None
            return None

    def get_next_page(self):
        """
        Возвращает следующую страницу по порядку или дате создания.

        Логика поиска:
        1. Ищем страницы с большим значением order
        2. Если не найдено, ищем по более поздней дате создания
        3. Возвращает первую найденную или None

        Возвращает:
            Page или None: Следующая страница или None если не найдена
        """
        try:
            # Пытаемся найти по порядку (основной критерий)
            next_page = (
                Page.objects.filter(show_on_site=True, order__gt=self.order)
                .order_by(
                    "order", "created_at"
                )  # Сортируем по возрастанию order и даты
                .first()
            )

            if not next_page:
                # Если не нашли по order, ищем по дате создания
                next_page = (
                    Page.objects.filter(
                        show_on_site=True, created_at__gt=self.created_at
                    )
                    .order_by("created_at")  # Сортируем по возрастанию даты
                    .first()
                )
            return next_page
        except Exception:
            # В случае ошибки возвращаем None
            return None

    @property
    def display_title(self):
        """
        Свойство: возвращает заголовок для отображения.

        Логика:
        - Если задан SEO заголовок, используем его
        - Иначе используем обычный заголовок

        Возвращает:
            str: Заголовок для отображения
        """
        return self.seo_title or self.title  # Используем SEO заголовок или обычный

    def clean(self):
        """
        Валидация данных страницы перед сохранением.
        Проверяет бизнес-правила и ограничения.

        Действия:
        1. Проверяет, что slug не зарезервирован системой
        2. Вызывает родительский метод clean()
        """
        super().clean()  # Вызываем валидацию родительского класса

        # Запрет использования зарезервированных URL
        reserved_slugs = ["admin", "login", "logout", "password"]
        # Список URL, которые нельзя использовать для страниц
        if self.slug in reserved_slugs:
            # Если slug в списке запрещенных, вызываем ошибку
            raise ValidationError({"slug": _("Этот URL-адрес зарезервирован системой")})


# Модель для управления файлами через админку Django
class ManagedFile(models.Model):
    """
    Модель для управления файлами через админку Django.
    Позволяет отслеживать, редактировать и создавать резервные копии файлов на диске.
    Предоставляет веб-интерфейс для файлового менеджера.
    """

    # Категории файлов
    CATEGORY_CHOICES = [
        ("log", _("Лог-файлы")),  # Файлы журналов
        ("config", _("Конфигурационные")),  # Конфигурационные файлы
        ("template", _("Шаблоны")),  # HTML шаблоны
        ("static", _("Статические")),  # Статические файлы (CSS, JS)
        ("media", _("Медиа")),  # Медиа файлы (изображения, видео)
        ("database", _("Базы данных")),  # Файлы баз данных
        ("backup", _("Резервные копии")),  # Резервные копии
        ("other", _("Другие")),  # Прочие файлы
    ]
    # Список возможных категорий файлов

    # Основные поля
    name = models.CharField(_("Имя файла"), max_length=255)
    # Имя файла для отображения в интерфейсе

    file_path = models.CharField(_("Полный путь"), max_length=500, unique=True)
    # Абсолютный путь к файлу на диске, должен быть уникальным

    category = models.CharField(
        _("Категория"), max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    # Категория файла из предопределенного списка

    description = models.TextField(_("Описание"), blank=True)
    # Дополнительное описание файла

    is_active = models.BooleanField(_("Активен"), default=True)
    # Флаг активности файла (можно временно отключить)

    is_text_file = models.BooleanField(_("Текстовый файл"), default=True)
    # Флаг, указывающий является ли файл текстовым

    encoding = models.CharField(_("Кодировка"), max_length=50, default="utf-8")
    # Кодировка текстового файла (utf-8, windows-1251 и т.д.)

    auto_backup = models.BooleanField(_("Авто-бэкап"), default=True)
    # Флаг автоматического создания резервных копий при изменении

    max_backups = models.IntegerField(_("Макс. бэкапов"), default=5)
    # Максимальное количество хранимых резервных копий

    # Информация о файле
    file_size = models.BigIntegerField(_("Размер файла"), default=0)
    # Размер файла в байтах

    file_mtime = models.DateTimeField(_("Время изменения"), null=True, blank=True)
    # Дата и время последнего изменения файла на диске

    mime_type = models.CharField(_("MIME тип"), max_length=100, blank=True)
    # MIME-тип файла (text/plain, image/jpeg и т.д.)

    file_permissions = models.CharField(_("Права доступа"), max_length=10, blank=True)
    # Права доступа к файлу в формате Unix (например, "644")

    # Содержимое файла (только для текстовых файлов)
    content = models.TextField(_("Содержимое"), blank=True, null=True)
    # Содержимое текстового файла (хранится в базе данных)

    # Системные поля
    last_checked = models.DateTimeField(_("Последняя проверка"), auto_now=True)
    # Дата и время последней проверки файла на диске

    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    # Дата и время создания записи в базе данных

    class Meta:
        """Метаданные модели управляемых файлов."""

        verbose_name = _("Управляемый файл")  # Имя в единственном числе
        verbose_name_plural = _("Управляемые файлы")  # Имя во множественном числе
        ordering = ["name"]  # Сортировка по умолчанию по имени

    def __str__(self):
        """
        Возвращает строковое представление файла.

        Возвращает:
            str: "Имя файла (Категория)"
        """
        return f"{self.name} ({self.get_category_display()})"

    @property
    def exists(self):
        """
        Свойство: проверяет, существует ли файл на диске.

        Действия:
        1. Проверяет не пустой ли путь
        2. Проверяет существование файла по указанному пути

        Возвращает:
            bool: True если файл существует, False в противном случае
        """
        return os.path.exists(self.file_path) if self.file_path else False
        # Используем os.path.exists для проверки существования файла

    @property
    def human_readable_size(self):
        """
        Свойство: возвращает размер файла в удобочитаемом формате.

        Преобразует байты в KB, MB, GB, TB.

        Возвращает:
            str: Размер с единицей измерения (например, "1.45 MB")
        """
        if not self.file_size:
            return "0 B"  # Если размер 0, возвращаем "0 B"

        size = float(self.file_size)  # Преобразуем в float для деления
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            # Перебираем единицы измерения
            if size < 1024.0:
                # Если размер меньше 1024 в текущих единицах, возвращаем
                return f"{size:.2f} {unit}"
            size /= 1024.0  # Переводим в следующую единицу измерения
        return f"{size:.2f} PB"  # Если очень большой, возвращаем PB (петабайты)

    def get_category_display(self):
        """
        Возвращает отображаемое имя категории.

        Действия:
        1. Преобразует внутренний код категории в читаемое имя
        2. Использует словарь CATEGORY_CHOICES

        Возвращает:
            str: Человекочитаемое имя категории
        """
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        # Используем словарь для преобразования кода в название

    def refresh_file_info(self):
        """
        Обновляет информацию о файле с диска.

        Действия:
        1. Проверяет существование файла
        2. Получает размер, дату изменения, права доступа
        3. Определяет MIME-тип
        4. Проверяет является ли файл текстовым
        5. Загружает содержимое для текстовых файлов (до 5MB)
        6. Сохраняет обновленные данные

        Возвращает:
            tuple: (success: bool, message: str)
        """
        try:
            # Проверяем существование файла
            if not self.file_path or not os.path.exists(self.file_path):
                return False, "Файл не существует"

            # Получаем информацию о файле с помощью os.stat
            stat_info = os.stat(self.file_path)
            self.file_size = stat_info.st_size  # Размер в байтах
            self.file_mtime = timezone.make_aware(
                datetime.fromtimestamp(stat_info.st_mtime)
            )  # Время изменения с учетом часового пояса

            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(self.file_path)
            # Функция guess_type пытается определить тип по расширению
            self.mime_type = mime_type or "application/octet-stream"
            # Если не удалось определить, используем стандартный тип

            # Определяем права доступа
            self.file_permissions = oct(stat_info.st_mode)[-3:]
            # Преобразуем режим доступа в восьмеричную систему и берем последние 3 цифры

            # Проверяем, текстовый ли файл
            self.is_text_file = self._check_if_text_file()

            # Загружаем содержимое для текстовых файлов
            if self.is_text_file and self.file_size < 5 * 1024 * 1024:  # 5 MB limit
                # Загружаем только если файл меньше 5MB
                try:
                    with open(
                        self.file_path, "r", encoding=self.encoding, errors="replace"
                    ) as f:
                        self.content = f.read()  # Читаем содержимое файла
                except (UnicodeDecodeError, IOError):
                    # Если ошибка декодирования, считаем файл бинарным
                    self.is_text_file = False
                    self.content = None
            else:
                self.content = (
                    None  # Не загружаем содержимое больших или бинарных файлов
                )

            self.save()  # Сохраняем обновленную информацию в базу
            return True, "Информация обновлена"

        except Exception as e:
            # Обрабатываем любые исключения
            return False, f"Ошибка: {str(e)}"

    def _check_if_text_file(self):
        """
        Приватный метод: проверяет, является ли файл текстовым.

        Алгоритм:
        1. Читает первые 1024 байта файла
        2. Проверяет наличие нулевых байтов (признак бинарного файла)
        3. Пытается декодировать как UTF-8

        Возвращает:
            bool: True если файл текстовый, False если бинарный
        """
        if not self.exists:
            return False  # Если файла нет, не можем проверить

        try:
            # Проверяем первые 1024 байта на наличие бинарных данных
            with open(self.file_path, "rb") as f:
                chunk = f.read(1024)  # Читаем первые 1024 байта

            # Если файл пустой, считаем его текстовым
            if not chunk:
                return True

            # Проверяем наличие нулевых байтов (признак бинарного файла)
            if b"\x00" in chunk:
                return False  # Найден нулевой байт - файл бинарный

            # Пытаемся декодировать как текст UTF-8
            try:
                chunk.decode("utf-8", errors="strict")
                return True  # Успешно декодировали - текстовый файл
            except UnicodeDecodeError:
                return False  # Не удалось декодировать - бинарный файл

        except Exception:
            # В случае ошибок чтения считаем файл бинарным
            return False

    def clear_file(self):
        """
        Очищает содержимое файла.

        Действия:
        1. Создает резервную копию (если включен auto_backup)
        2. Открывает файл в режиме записи и записывает пустую строку
        3. Обновляет информацию о файле

        Возвращает:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.exists:
                return False, "Файл не существует"

            # Создаем бэкап перед очисткой (если включено)
            if self.auto_backup:
                self.create_backup()

            # Очищаем файл (открываем в режиме записи и записываем пустую строку)
            with open(self.file_path, "w", encoding=self.encoding) as f:
                f.write("")

            # Обновляем информацию о файле
            self.refresh_file_info()
            return True, "Файл очищен"

        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def create_backup(self):
        """
        Создает резервную копию файла.

        Действия:
        1. Создает директорию backups рядом с файлом
        2. Генерирует имя с временной меткой
        3. Копирует файл с сохранением метаданных
        4. Очищает старые бэкапы сверх лимита

        Возвращает:
            tuple: (backup_path: str или None, message: str)
        """
        try:
            if not self.exists:
                return None, "Файл не существует"

            # Создаем директорию для бэкапов
            backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)  # Создаем если не существует

            # Генерируем имя файла для бэкапа с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(self.file_path)}.backup_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)

            # Копируем файл с сохранением метаданных (время, права доступа)
            shutil.copy2(self.file_path, backup_path)

            # Очищаем старые бэкапы (если превышен лимит)
            self.cleanup_old_backups(backup_dir)

            return backup_path, "Резервная копия создана"

        except Exception as e:
            return None, f"Ошибка создания бэкапа: {str(e)}"

    def cleanup_old_backups(self, backup_dir):
        """
        Очищает старые бэкапы, если превышен лимит.

        Действия:
        1. Находит все бэкапы текущего файла
        2. Сортирует по дате изменения (старые первыми)
        3. Удаляет самые старые сверх лимита max_backups

        Параметры:
            backup_dir: Путь к директории с бэкапами
        """
        try:
            if not os.path.exists(backup_dir):
                return  # Если директории нет, выходим

            base_name = os.path.basename(self.file_path)
            backup_pattern = os.path.join(backup_dir, f"{base_name}.backup_*")

            import glob  # Импортируем здесь, так как используется редко

            # Находим все бэкапы и сортируем по времени изменения (старые первыми)
            backups = sorted(glob.glob(backup_pattern), key=os.path.getmtime)

            # Удаляем старые бэкапы, если превышен лимит
            while len(backups) > self.max_backups:
                oldest_backup = backups.pop(0)  # Берем самый старый бэкап
                try:
                    os.remove(oldest_backup)  # Удаляем файл
                except Exception:
                    pass  # Игнорируем ошибки удаления

        except Exception as e:
            print(f"Ошибка очистки бэкапов: {e}")  # Логируем ошибку

    def get_backup_list(self):
        """
        Возвращает список резервных копий файла.

        Действия:
        1. Ищет бэкапы в директории backups
        2. Собирает информацию о каждом бэкапе
        3. Сортирует по дате изменения (новые первыми)

        Возвращает:
            list: Список словарей с информацией о бэкапах
        """
        backups = []  # Инициализируем пустой список
        try:
            backup_dir = os.path.join(os.path.dirname(self.file_path), "backups")
            if os.path.exists(backup_dir):
                import glob  # Импортируем здесь

                # Формируем шаблон для поиска бэкапов
                base_name = os.path.basename(self.file_path)
                backup_pattern = os.path.join(backup_dir, f"{base_name}.backup_*")

                # Находим все бэкапы и сортируем по дате изменения (новые первыми)
                for backup_path in sorted(
                    glob.glob(backup_pattern), key=os.path.getmtime, reverse=True
                ):
                    try:
                        stat_info = os.stat(backup_path)
                        # Собираем информацию о бэкапе
                        backups.append(
                            {
                                "path": backup_path,  # Полный путь
                                "name": os.path.basename(backup_path),  # Имя файла
                                "size": stat_info.st_size,  # Размер в байтах
                                "human_size": self._format_size(
                                    stat_info.st_size
                                ),  # Размер в читаемом формате
                                "modified": timezone.make_aware(
                                    datetime.fromtimestamp(stat_info.st_mtime)
                                ),  # Время изменения
                            }
                        )
                    except Exception:
                        continue  # Пропускаем бэкапы с ошибками
        except Exception as e:
            print(f"Ошибка получения списка бэкапов: {e}")  # Логируем ошибку

        return backups  # Возвращаем список бэкапов

    def _format_size(self, size):
        """
        Приватный метод: форматирует размер файла.

        Параметры:
            size: Размер в байтах

        Возвращает:
            str: Размер в удобочитаемом формате
        """
        for unit in ["B", "KB", "MB", "GB"]:
            # Перебираем единицы измерения
            if size < 1024.0:
                return f"{size:.1f} {unit}"  # Возвращаем с одним десятичным знаком
            size /= 1024.0  # Переводим в следующую единицу
        return f"{size:.1f} TB"  # Если очень большой, возвращаем TB

    def save_content(self, new_content):
        """
        Сохраняет новое содержимое в файл на диске.

        Действия:
        1. Создает резервную копию (если включен auto_backup)
        2. Записывает новое содержимое в файл
        3. Обновляет информацию о файле в БД

        Возвращает:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.exists:
                return False, "Файл не существует на диске"

            # Создаем бэкап
            if self.auto_backup:
                self.create_backup()

            # Записываем контент
            with open(self.file_path, "w", encoding=self.encoding) as f:
                f.write(new_content)

            # Обновляем инфо
            self.refresh_file_info()
            return True, "Содержимое файла успешно сохранено"

        except Exception as e:
            return False, f"Ошибка при сохранении файла: {str(e)}"

    def restore_backup(self, backup_path):
        """
        Восстанавливает файл из резервной копии.

        Параметры:
            backup_path: Путь к файлу бэкапа

        Возвращает:
            tuple: (success: bool, message: str)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Файл резервной копии не найден"

            # Копируем бэкап на место оригинала
            shutil.copy2(backup_path, self.file_path)

            # Обновляем инфо
            self.refresh_file_info()
            return True, "Файл успешно восстановлен из резервной копии"

        except Exception as e:
            return False, f"Ошибка при восстановлении: {str(e)}"

    def delete_file_from_disk(self):
        """
        Удаляет файл с диска.

        Действия:
        1. Создает резервную копию (если включен auto_backup)
        2. Удаляет файл с диска
        3. Сбрасывает информацию о файле в базе данных

        Возвращает:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.exists:
                return False, "Файл не существует"

            # Создаем бэкап перед удалением (если включено)
            if self.auto_backup:
                self.create_backup()

            # Удаляем файл с диска
            os.remove(self.file_path)

            # Сбрасываем информацию о файле в базе данных
            self.file_size = 0
            self.file_mtime = None
            self.mime_type = ""
            self.file_permissions = ""
            self.content = None
            self.save()  # Сохраняем изменения

            return True, "Файл удален с диска"

        except Exception as e:
            return False, f"Ошибка удаления файла: {str(e)}"

    @classmethod
    def get_existing_files(cls):
        """
        Классовый метод: возвращает QuerySet файлов с аннотацией существования.

        Действия:
        1. Аннотирует каждый файл полем exists_on_disk
        2. Определяет существует ли файл на диске

        Возвращает:
            QuerySet: QuerySet с аннотацией exists_on_disk
        """
        from django.db.models import Case, When, Value, BooleanField

        # Создаем сложную аннотацию для определения существования файла
        return cls.objects.all().annotate(
            exists_on_disk=Case(
                *[
                    When(file_path__isnull=True, then=Value(False)),  # Если путь None
                    When(file_path__exact="", then=Value(False)),  # Если путь пустой
                ],
                default=Value(True),  # По умолчанию считаем что файл существует
                output_field=BooleanField(),  # Тип поля - Boolean
            )
        )

    def get_files_exists_count(self):
        """
        Подсчитывает количество файлов, которые существуют на диске.

        Действия:
        1. Перебирает все файлы в базе
        2. Проверяет свойство exists для каждого
        3. Считает количество существующих файлов

        Возвращает:
            int: Количество существующих файлов
        """
        count = 0
        for obj in ManagedFile.objects.all():
            if obj.exists:  # Используем свойство exists
                count += 1
        return count


# Модель для хранения статистики лог-файлов
class LogStats(models.Model):
    """
    Модель для хранения статистики лог-файлов.
    Позволяет отслеживать и анализировать логи системы.
    Каждый день создается одна запись с агрегированной статистикой.
    """

    log_date = models.DateField(
        verbose_name="Дата логов",
        unique=True,  # Одна запись на дату
        help_text="Дата, за которую собрана статистика",
    )
    # Дата, за которую собрана статистика

    total_lines = models.IntegerField(
        verbose_name="Всего строк",
        default=0,
        help_text="Общее количество строк в лог-файле",
    )
    # Общее количество строк в логе за день

    error_count = models.IntegerField(
        verbose_name="Ошибки", default=0, help_text="Количество строк с ошибками"
    )
    # Количество строк содержащих ошибки (уровень ERROR)

    warning_count = models.IntegerField(
        verbose_name="Предупреждения",
        default=0,
        help_text="Количество строк с предупреждениями",
    )
    # Количество строк содержащих предупреждения (уровень WARNING)

    info_count = models.IntegerField(
        verbose_name="Информационные",
        default=0,
        help_text="Количество информационных строк",
    )
    # Количество информационных строк (уровень INFO)

    debug_count = models.IntegerField(
        verbose_name="Отладочные", default=0, help_text="Количество отладочных строк"
    )
    # Количество отладочных строк (уровень DEBUG)

    other_count = models.IntegerField(
        verbose_name="Прочие", default=0, help_text="Количество строк других типов"
    )
    # Количество строк других типов или без указания уровня

    created_at = models.DateTimeField(verbose_name="Создано", auto_now_add=True)
    # Дата и время создания записи статистики

    updated_at = models.DateTimeField(verbose_name="Обновлено", auto_now=True)
    # Дата и время последнего обновления статистики

    class Meta:
        """Метаданные модели статистики логов."""

        verbose_name = "Статистика логов"  # Имя в единственном числе
        verbose_name_plural = "Статистика логов"  # Имя во множественном числе
        ordering = ["-log_date"]  # Сортировка по убыванию даты (новые первыми)

    def __str__(self):
        """
        Возвращает строковое представление статистики.

        Возвращает:
            str: "Статистика логов за ДАТА"
        """
        return f"Статистика логов за {self.log_date}"


# Прокси-модель для LogStats, чтобы отобразить отдельный пункт
# меню для управления логом ошибок (error.log).
class ErrorLog(LogStats):
    """
    Прокси-модель для LogStats, чтобы отобразить отдельный пункт
    меню для управления логом ошибок (error.log).
    """

    class Meta:
        proxy = True
        verbose_name = "Лог ошибок"
        verbose_name_plural = "Лог ошибок"


# Модель для статистических баннеров (Яндекс.Метрика, Google Analytics и др.).
class StatisticsBanner(models.Model):
    """
    Модель для статистических баннеров (Яндекс.Метрика, Google Analytics и др.).
    """
    
    BANNER_TYPES = [
        ('yandex_metrika', _('Яндекс.Метрика')),
        ('google_analytics', _('Google Analytics')),
        ('google_tag_manager', _('Google Tag Manager')),
        ('facebook_pixel', _('Facebook Pixel')),
        ('vk_retargeting', _('VK Ретаргетинг')),
        ('mailru_top', _('Mail.ru Top')),
        ('liveinternet', _('LiveInternet')),
        ('custom', _('Пользовательский код')),
        ('other', _('Другой')),
    ]
    
    POSITIONS = [
        ('head', _('В <head> (рекомендуется для счетчиков)')),
        ('body_start', _('В начале <body>')),
        ('body_end', _('В конце <body> (рекомендуется для скриптов)')),
        ('header', _('В шапке сайта')),
        ('footer', _('В подвале сайта')),
        ('custom', _('Кастомная позиция (вручную в шаблоне)')),
    ]
    
    # Основные поля
    name = models.CharField(
        _('Название баннера'),
        max_length=200,
        help_text=_('Например: Яндекс.Метрика главный счетчик')
    )
    
    banner_type = models.CharField(
        _('Тип баннера'),
        max_length=50,
        choices=BANNER_TYPES,
        default='yandex_metrika'
    )
    
    code = models.TextField(
        _('Код баннера'),
        help_text=_('HTML/JavaScript код для вставки на сайт')
    )
    
    position = models.CharField(
        _('Позиция на странице'),
        max_length=50,
        choices=POSITIONS,
        default='head'
    )
    
    # Настройки видимости
    is_active = models.BooleanField(
        _('Активен'),
        default=True,
        help_text=_('Включить/выключить баннер')
    )
    
    show_on_all_pages = models.BooleanField(
        _('Показывать на всех страницах'),
        default=True,
        help_text=_('Если включено, баннер будет отображаться на всех страницах сайта')
    )
    
    show_on_index = models.BooleanField(
        _('Показывать на главной'),
        default=True
    )
    
    show_on_pages = models.BooleanField(
        _('Показывать на страницах'),
        default=True
    )
    
    show_on_news = models.BooleanField(
        _('Показывать на новостях'),
        default=True
    )
    
    show_on_portfolio = models.BooleanField(
        _('Показывать на портфолио'),
        default=True
    )
    
    # Дополнительные настройки
    enabled_for_admin = models.BooleanField(
        _('Показывать администраторам'),
        default=False,
        help_text=_('Если включено, баннер будет виден администраторам сайта')
    )
    
    enabled_for_staff = models.BooleanField(
        _('Показывать персоналу'),
        default=False,
        help_text=_('Если включено, баннер будет виден персоналу сайта')
    )
    
    enabled_for_users = models.BooleanField(
        _('Показывать пользователям'),
        default=True,
        help_text=_('Если включено, баннер будет виден обычным пользователям')
    )
    
    # Приоритет и сортировка
    order = models.IntegerField(
        _('Порядок отображения'),
        default=0,
        help_text=_('Чем меньше число, тем выше баннер в списке')
    )
    
    # Информация о счетчике
    counter_id = models.CharField(
        _('ID счетчика'),
        max_length=100,
        blank=True,
        help_text=_('ID счетчика Яндекс.Метрики, Google Analytics и т.д.')
    )
    
    description = models.TextField(
        _('Описание'),
        blank=True,
        help_text=_('Дополнительная информация о баннере')
    )
    
    # Временные метки
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)
    
    class Meta:
        verbose_name = _('Статистический баннер')
        verbose_name_plural = _('Статистические баннеры')
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_banner_type_display()})"
    
    def clean(self):
        """Валидация данных баннера."""
        super().clean()
        
        # Проверяем, что для Яндекс.Метрики указан ID счетчика
        if self.banner_type == 'yandex_metrika' and not self.counter_id:
            raise ValidationError({
                'counter_id': _('Для Яндекс.Метрики необходимо указать ID счетчика')
            })
        
        # Проверяем, что код не пустой
        if not self.code.strip():
            raise ValidationError({
                'code': _('Код баннера не может быть пустым')
            })
    
    def get_rendered_code(self, request=None):
        """
        Возвращает готовый для вставки код с учетом настроек видимости.
        
        Args:
            request: Объект запроса для проверки прав пользователя
            
        Returns:
            str: HTML код для вставки или пустая строка
        """
        # Проверяем активность баннера
        if not self.is_active:
            return ""
        
        # Проверяем права доступа
        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_authenticated:
                if user.is_superuser and not self.enabled_for_admin:
                    return ""
                if user.is_staff and not self.enabled_for_staff:
                    return ""
                if not user.is_staff and not user.is_superuser and not self.enabled_for_users:
                    return ""
        
        # Возвращаем код баннера
        return self.code.strip()