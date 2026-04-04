# news/models.py
# Модели для приложения news (новости)
from django.db import models  # Импорт базовых моделей Django
from django.db.models import F  # Атомарное обновление полей
from django.urls import reverse  # Функция для генерации URL
from django.utils.text import (
    slugify,
)  # Функция для преобразования строки в slug (URL-дружественный формат)
from django_ckeditor_5.fields import (
    CKEditor5Field,
)  # Поле для расширенного текстового редактора

from main.models import HeroMixin


class NewsTag(models.Model):
    """
    Тег (метка) для новостей.
    Используется для группировки новостей по темам и улучшения SEO.
    """

    name = models.CharField("Название тега", max_length=50, unique=True)
    slug = models.SlugField("Слаг", max_length=50, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:by_tag", kwargs={"slug": self.slug})


class NewsCategory(HeroMixin):
    """
    Категория новостей.
    Модель для группировки новостей по темам.
    """

    # Основные поля
    name = models.CharField(
        "Название", max_length=100
    )  # Название категории, максимум 100 символов
    slug = models.SlugField(
        "URL", unique=True
    )  # URL-дружественный идентификатор, должен быть уникальным
    image = models.ImageField(
        "Изображение", upload_to="news/categories/", blank=True
    )  # Изображение категории, может быть пустым
    description = CKEditor5Field(
        "Описание", blank=True, config_name="extends"
    )  # Описание категории с расширенным редактором, может быть пустым

    # СЕО поля (для поисковой оптимизации)
    seo_title = models.CharField(
        "SEO заголовок", max_length=200, blank=True
    )  # SEO заголовок для поисковых систем, может быть пустым
    seo_keywords = models.CharField(
        "SEO ключевые слова", max_length=200, blank=True
    )  # Ключевые слова для SEO, могут быть пустыми
    seo_description = models.CharField(
        "SEO описание", max_length=255, blank=True
    )  # SEO описание для поисковых систем, может быть пустым

    # Настройки отображения
    show_in_menu = models.BooleanField(
        "Показывать в меню", default=True
    )  # Показывать ли категорию в меню (по умолчанию да)
    order = models.IntegerField(
        "Порядок", default=0
    )  # Порядок отображения категории в меню (чем меньше, тем выше)
    is_active = models.BooleanField(
        "Активно", default=True
    )  # Активна ли категория (по умолчанию да)
    views = models.PositiveIntegerField(
        "Просмотры", default=0
    )  # Количество просмотров категории

    class Meta:
        """Метаданные модели категории новостей."""

        verbose_name = "Категория новостей"  # Единственное число для админки
        verbose_name_plural = "Категории новостей"  # Множественное число для админки
        ordering = [
            "order",
            "name",
        ]  # Сортировка по порядку (возрастание) и имени (алфавитный порядок)

    def __str__(self):
        """Строковое представление объекта для отображения в админке и консоли."""
        return self.name  # Возвращаем название категории

    def save(self, *args, **kwargs):
        """
        Создаем slug из названия, если он не задан.
        ИСПРАВЛЕНО: При проверке уникальности исключаем текущий объект.
        """
        if not self.slug:
            base_slug = slugify(self.name)  # Преобразуем название в slug
            self.slug = base_slug  # Устанавливаем базовый slug
            # Убеждаемся, что slug уникален (исключаем текущий объект при обновлении)
            counter = 1
            # ИСПРАВЛЕНО: Добавлен фильтр для исключения текущего объекта при проверке уникальности
            queryset = NewsCategory.objects.filter(slug=self.slug)
            if self.pk:  # Если объект уже существует (обновление)
                queryset = queryset.exclude(pk=self.pk)  # Исключаем текущий объект
            while queryset.exists():  # Пока slug не уникален
                self.slug = f"{base_slug}-{counter}"  # Добавляем номер к slug
                queryset = NewsCategory.objects.filter(slug=self.slug)
                if self.pk:  # Если объект уже существует
                    queryset = queryset.exclude(pk=self.pk)  # Исключаем текущий объект
                counter += 1  # Увеличиваем счетчик
        super().save(*args, **kwargs)  # Вызываем метод save родительского класса

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для просмотра категории.
        Используется в админке и шаблонах.

        Returns:
            str: URL страницы категории новостей
        """
        return reverse(
            "news:category", kwargs={"slug": self.slug}
        )  # Генерируем URL используя имя маршрута и slug категории


class News(HeroMixin):
    """
    Новость.
    Модель для хранения новостных статей на сайте.
    """

    # Основные поля
    title = models.CharField(
        "Заголовок", max_length=200
    )  # Заголовок новости, максимум 200 символов
    slug = models.SlugField(
        "URL", unique=True
    )  # URL-дружественный идентификатор, должен быть уникальным
    category = models.ForeignKey(
        NewsCategory,  # Связь многие-к-одному с моделью NewsCategory
        on_delete=models.PROTECT,  # Защита: нельзя удалить категорию, пока в ней есть новости
        verbose_name="Категория",
    )
    image = models.ImageField(
        "Изображение",  # Человекочитаемое имя поля
        upload_to="news/",  # Папка для загрузки изображений новостей
        default="news/default-category.png",  # Изображение по умолчанию, если не указано
        help_text="Оставьте стандартное изображение, чтобы использовать картинку из категории",
    )
    is_active = models.BooleanField(
        "Активно", default=True
    )  # Активна ли новость (по умолчанию да)

    # SEO поля (для поисковой оптимизации)
    seo_title = models.CharField(
        "SEO заголовок", max_length=200, blank=True
    )  # SEO заголовок для поисковых систем, может быть пустым
    seo_keywords = models.CharField(
        "SEO ключевые слова", max_length=200, blank=True
    )  # Ключевые слова для SEO, могут быть пустыми
    seo_description = models.CharField(
        "SEO описание", max_length=255, blank=True
    )  # SEO описание для поисковых систем, может быть пустым

    # Контент
    short_description = CKEditor5Field(
        "Краткое описание",  # Человекочитаемое имя поля
        blank=True,  # Поле может быть пустым
        config_name="extends",  # Использовать расширенную конфигурацию редактора
    )
    content = CKEditor5Field(
        "Содержание", blank=True, config_name="extends"
    )  # Полное содержание новости с расширенным редактором, может быть пустым

    # Теги для улучшения навигации и SEO
    tags = models.ManyToManyField(
        NewsTag,
        verbose_name="Теги",
        blank=True,
        related_name="news",
    )

    # Системные поля
    views = models.PositiveIntegerField(
        "Просмотры", default=0
    )  # Счетчик просмотров новости (только положительные числа, по умолчанию 0)
    created_at = models.DateTimeField(
        "Создано", auto_now_add=True
    )  # Дата и время создания (устанавливается автоматически)
    updated_at = models.DateTimeField(
        "Обновлено", auto_now=True
    )  # Дата и время последнего обновления (обновляется автоматически)

    class Meta:
        """Метаданные модели новости."""

        verbose_name = "Новость"  # Единственное число для админки
        verbose_name_plural = "Новости"  # Множественное число для админки
        ordering = [
            "-created_at"
        ]  # Сортировка по дате создания (новые сверху, знак минус означает убывание)

    def __str__(self):
        """Строковое представление объекта для отображения в админке и консоли."""
        return self.title  # Возвращаем заголовок новости

    def save(self, *args, **kwargs):
        """
        Создаем slug из заголовка, если он не задан.
        Автоматически устанавливаем изображение из категории, если свое не задано.
        Умное наследование: если категория меняется и изображение было унаследовано от старой,
        оно обновится на изображение новой категории.
        """
        if self.category:
            # 1. Если изображение не задано или является основным дефолтным
            if not self.image or self.image.name == 'news/default-category.png':
                if self.category.image:
                    self.image = self.category.image
            
            # 2. Если объект уже существует, проверяем, не сменилась ли категория
            elif self.pk:
                try:
                    old_instance = News.objects.get(pk=self.pk)
                    # Если категория изменилась
                    if old_instance.category_id != self.category_id:
                        # Проверяем, было ли текущее изображение унаследовано от старой категории
                        if old_instance.category and old_instance.category.image and \
                           self.image.name == old_instance.category.image.name:
                            # Да, это было наследство. Обновляем его из новой категории (или ставим дефолт)
                            if self.category.image:
                                self.image = self.category.image
                            else:
                                self.image = 'news/default-category.png'
                except News.DoesNotExist:
                    pass

            # Аналогичная логика для Hero-изображения
            if not self.hero_image and self.category.hero_image:
                self.hero_image = self.category.hero_image
            elif self.pk:
                try:
                    old_instance = News.objects.get(pk=self.pk)
                    if old_instance.category_id != self.category_id:
                        if old_instance.category and old_instance.category.hero_image and \
                           self.hero_image.name == old_instance.category.hero_image.name:
                            if self.category.hero_image:
                                self.hero_image = self.category.hero_image
                            else:
                                self.hero_image = None
                except News.DoesNotExist:
                    pass

        if not self.slug:
            base_slug = slugify(self.title)  # Преобразуем заголовок в slug
            self.slug = base_slug  # Устанавливаем базовый slug
            # Убеждаемся, что slug уникален (исключаем текущий объект при обновлении)
            counter = 1
            # ИСПРАВЛЕНО: Добавлен фильтр для исключения текущего объекта при проверке уникальности
            queryset = News.objects.filter(slug=self.slug)
            if self.pk:  # Если объект уже существует (обновление)
                queryset = queryset.exclude(pk=self.pk)  # Исключаем текущий объект
            while queryset.exists():  # Пока slug не уникален
                self.slug = f"{base_slug}-{counter}"  # Добавляем номер к slug
                queryset = News.objects.filter(slug=self.slug)
                if self.pk:  # Если объект уже существует
                    queryset = queryset.exclude(pk=self.pk)  # Исключаем текущий объект
                counter += 1  # Увеличиваем счетчик
        super().save(*args, **kwargs)  # Вызываем метод save родительского класса

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для просмотра новости.
        Используется в админке и шаблонах.

        Returns:
            str: URL страницы детального просмотра новости
        """
        return reverse(
            "news:detail", kwargs={"slug": self.slug}
        )  # Генерируем URL используя имя маршрута и slug новости

    def increment_views(self):
        """
        Атомарно увеличивает счётчик просмотров на 1.
        Использует F() для защиты от race condition при одновременных запросах.
        """
        News.objects.filter(pk=self.pk).update(views=F("views") + 1)
        self.refresh_from_db(fields=["views"])
