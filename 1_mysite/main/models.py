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
from django.utils.translation import (
    gettext_lazy as _,
)  # Функция для интернационализации строк
from django.urls import reverse  # Функция для построения абсолютных URL
from django_ckeditor_5.fields import (
    CKEditor5Field,
)  # Поле WYSIWYG редактора для контента
from datetime import datetime  # Класс для работы с датой и временем
from pathlib import Path  # Современный класс для работы с путями к файлам
from django.db import models  # Базовые классы моделей Django ORM
from django.core.files.base import ContentFile  # Класс для работы с файловым содержимым
from django.utils import timezone  # Утилиты для работы с часовыми поясами
from django.conf import settings  # Настройки Django проекта
from django.core.exceptions import ValidationError  # Исключение для ошибок валидации
from django.utils.html import format_html  # Функция для безопасного форматирования HTML


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


class SiteSettings(SingletonModel):
    """
    Модель для хранения глобальных настроек сайта.
    Наследует SingletonModel для гарантии единственного экземпляра.
    Содержит контакты, логотип, SEO-настройки и статус сайта.
    """

    # Контактная информация
    phone1 = models.CharField(_("Основной телефон"), max_length=20, blank=True)
    # Поле для основного телефона, максимальная длина 20 символов, может быть пустым

    phone2 = models.CharField(_("Дополнительный телефон"), max_length=20, blank=True)
    # Поле для дополнительного телефона

    email = models.EmailField(_("Электронная почта"), max_length=255, blank=True)
    # Поле для email с валидацией формата

    address = models.CharField(_("Адрес"), max_length=255, blank=True)
    # Текстовое поле для физического адреса

    # Брендинг и контент
    logo = models.ImageField(
        _("Логотип"),
        upload_to="logos/",  # Файлы сохраняются в MEDIA_ROOT/logos/
        blank=True,
        help_text=_("Рекомендуемый размер: 200x60 пикселей"),
    )
    # Поле для загрузки изображения логотипа

    logo_text = models.CharField(_("Текст логотипа"), max_length=100, blank=True)
    # Текстовое представление логотипа (для SEO и доступности)

    slogan = models.CharField(_("Слоган"), max_length=255, blank=True)
    # Короткий слоган компании

    motto = CKEditor5Field(_("Девиз сайта"), blank=True, config_name="extends")
    # Расширенный девиз с поддержкой WYSIWYG редактора

    short_description = CKEditor5Field(
        _("Краткое описание"), blank=True, config_name="extends"
    )
    # Краткое описание сайта для главной страницы

    content = CKEditor5Field(_("Основной контент"), blank=True, config_name="extends")
    # Основной контент для страниц

    # Социальные сети
    facebook = models.URLField(_("Facebook"), blank=True)
    # Ссылка на Facebook

    instagram = models.URLField(_("Instagram"), blank=True)
    # Ссылка на Instagram

    youtube = models.URLField(_("YouTube"), blank=True)
    # Ссылка на YouTube

    rutube = models.URLField(_("Rutube"), blank=True)
    # Ссылка на Rutube

    vk_video = models.URLField(_("VK Видео"), blank=True)
    # Ссылка на VK Видео

    telegram = models.URLField(_("Telegram"), blank=True)
    # Ссылка на Telegram

    vk = models.URLField(_("ВКонтакте"), blank=True)
    # Ссылка на ВКонтакте

    ok = models.URLField(_("Одноклассники"), blank=True)
    # Ссылка на Одноклассники

    # SEO оптимизация
    seo_title = models.CharField(
        _("SEO заголовок (title)"),
        max_length=200,
        blank=True,
        help_text=_("Если не указан, используется заголовок страницы"),
    )
    # Заголовок для SEO и вкладки браузера

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

    # Статус сайта
    site_closed = models.BooleanField(_("Сайт закрыт"), default=False)
    # Флаг, указывающий закрыт ли сайт на обслуживание

    closure_message = models.TextField(
        _("Сообщение при закрытии"),
        blank=True,
        help_text=_("Сообщение, которое увидят пользователи при закрытии сайта"),
    )
    # Сообщение для пользователей при закрытом сайте

    # Временные метки
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    # Дата и время создания (заполняется автоматически при создании)

    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)
    # Дата и время последнего обновления (автоматически обновляется)

    class Meta:
        """Метаданные модели настроек сайта."""

        verbose_name = _("Настройки сайта")  # Имя в единственном числе
        verbose_name_plural = _("Настройки сайта")  # Имя во множественном числе

    def __str__(self):
        """
        Возвращает строковое представление объекта.

        Возвращает:
            str: "Настройки сайта" (переведенная строка)
        """
        return str(_("Настройки сайта"))  # Явное преобразование в строку

    def clean(self):
        """
        Валидация данных перед сохранением.
        Проверяет корректность данных и бизнес-правила.

        Действия:
        1. Проверяет наличие сообщения при закрытии сайта
        2. Валидирует email адрес
        3. Вызывает родительский метод clean()
        """
        super().clean()  # Вызываем валидацию родительского класса

        # Проверка наличия сообщения при закрытии сайта
        if self.site_closed and not self.closure_message:
            # Если сайт закрыт, но сообщение не указано - ошибка
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
            # Проверяем базовый формат email
            raise ValidationError({"email": _("Введите корректный email адрес")})


class Page(models.Model):
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
        from django.db.models import Q, Case, When, Value, BooleanField

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
