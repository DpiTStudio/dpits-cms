# news/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class NewsCategory(models.Model):
    """Модель категории новостей"""

    # Основные поля
    name = models.CharField(_("Название"), max_length=100)  # Название категории
    slug = models.SlugField(_("URL"), unique=True)  # URL-идентификатор для ЧПУ
    image = models.ImageField(
        _("Изображение"), upload_to="news/categories/", blank=True
    )  # Изображение категории
    description = CKEditor5Field(
        _("Описание"), blank=True, config_name="extends"
    )  # Описание с WYSIWYG редактором
    show_in_menu = models.BooleanField(
        _("Показывать в меню"), default=True
    )  # Показывать в меню навигации
    order = models.IntegerField(_("Порядок"), default=0)  # Порядок сортировки
    is_active = models.BooleanField(_("Активно"), default=True)  # Активна ли категория

    class Meta:
        verbose_name = _(
            "Категория новостей"
        )  # Человекочитаемое имя в единственном числе
        verbose_name_plural = _(
            "Категории новостей"
        )  # Человекочитаемое имя во множественном числе
        ordering = ["order", "name"]  # Сортировка по порядку и имени

    def __str__(self):
        """Строковое представление объекта"""
        return self.name

    def save(self, *args, **kwargs):
        """Автоматическое создание slug при сохранении"""
        if not self.slug:
            self.slug = slugify(self.name)  # Генерация slug из названия
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Получение абсолютного URL для категории"""
        return reverse("news:category", kwargs={"slug": self.slug})


class News(models.Model):
    """Модель новости"""

    # Основные поля
    title = models.CharField(_("Заголовок"), max_length=200)  # Заголовок новости
    slug = models.SlugField(_("URL"), unique=True)  # URL-идентификатор
    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, verbose_name=_("Категория")
    )  # Связь с категорией (удаление каскадом)
    image = models.ImageField(
        _("Изображение"), upload_to="news/"
    )  # Главное изображение
    is_active = models.BooleanField(_("Активно"), default=True)  # Активна ли новость

    # SEO поля
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)

    # Контентные поля
    short_description = CKEditor5Field(
        _("Краткое описание"), blank=True, config_name="extends"
    )  # Краткое описание с редактором
    content = CKEditor5Field(
        _("Содержание"), blank=True, config_name="extends"
    )  # Полное содержание

    # Системные поля
    views = models.PositiveIntegerField(_("Просмотры"), default=0)  # Счетчик просмотров
    created_at = models.DateTimeField(
        _("Создано"), auto_now_add=True
    )  # Дата создания (только при создании)
    updated_at = models.DateTimeField(
        _("Обновлено"), auto_now=True
    )  # Дата обновления (при каждом сохранении)

    class Meta:
        verbose_name = _("Новость")  # Человекочитаемое имя в единственном числе
        verbose_name_plural = _(
            "Новости"
        )  # Человекочитаемое имя во множественном числе
        ordering = ["-created_at"]  # Сортировка по дате создания (новые сначала)

    def __str__(self):
        """Строковое представление объекта"""
        return self.title

    def save(self, *args, **kwargs):
        """Автоматическое создание slug при сохранении"""
        if not self.slug:
            self.slug = slugify(self.title)  # Генерация slug из заголовка
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Получение абсолютного URL для новости"""
        return reverse("news:detail", kwargs={"slug": self.slug})

    def increment_views(self):
        """Увеличение счетчика просмотров на 1"""
        self.views += 1
        self.save(
            update_fields=["views"]
        )  # Сохранение только поля views для оптимизации
