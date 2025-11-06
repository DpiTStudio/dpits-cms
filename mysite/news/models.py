# news/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class NewsCategory(models.Model):
    """Категория новостей"""

    # Основные поля
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", unique=True)
    image = models.ImageField("Изображение", upload_to="news/categories/", blank=True)
    description = CKEditor5Field("Описание", blank=True, config_name="extends")

    # Настройки отображения
    show_in_menu = models.BooleanField("Показывать в меню", default=True)
    order = models.IntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"
        ordering = ["order", "name"]  # Сортировка по порядку и имени

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Создаем slug из названия, если он не задан"""
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            # Убеждаемся, что slug уникален
            counter = 1
            while NewsCategory.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """URL для категории"""
        return reverse("news:category", kwargs={"slug": self.slug})


class News(models.Model):
    """Новость"""

    # Основные поля
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", unique=True)
    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, verbose_name="Категория"
    )
    image = models.ImageField("Изображение", upload_to="news/")
    is_active = models.BooleanField("Активно", default=True)

    # SEO поля
    seo_title = models.CharField("SEO заголовок", max_length=200, blank=True)
    seo_keywords = models.CharField("SEO ключевые слова", max_length=200, blank=True)
    seo_description = models.CharField("SEO описание", max_length=255, blank=True)

    # Контент
    short_description = CKEditor5Field(
        "Краткое описание", blank=True, config_name="extends"
    )
    content = CKEditor5Field("Содержание", blank=True, config_name="extends")

    # Системные поля
    views = models.PositiveIntegerField("Просмотры", default=0)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]  # Новые сверху

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Создаем slug из заголовка, если он не задан"""
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            # Убеждаемся, что slug уникален
            counter = 1
            while News.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """URL для новости"""
        return reverse("news:detail", kwargs={"slug": self.slug})

    def increment_views(self):
        """Увеличиваем счетчик просмотров"""
        self.views += 1
        self.save(update_fields=["views"])  # Сохраняем только поле views
