# news/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
# from tinymce.models import HTMLField


class NewsCategory(models.Model):
    name = models.CharField(_("Название"), max_length=100)
    slug = models.SlugField(_("URL"), unique=True)
    image = models.ImageField(
        _("Изображение"), upload_to="news/categories/", blank=True
    )
    description = CKEditor5Field(_("Описание"), blank=True, config_name="extends")
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    order = models.IntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)

    class Meta:
        verbose_name = _("Категория новостей")
        verbose_name_plural = _("Категории новостей")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:category", kwargs={"slug": self.slug})


class News(models.Model):
    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True)
    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, verbose_name=_("Категория")
    )
    image = models.ImageField(_("Изображение"), upload_to="news/")
    short_description = models.TextField(_("Краткое описание"))
    content = CKEditor5Field(_("Содержание"), blank=True, config_name="extends")
    views = models.PositiveIntegerField(_("Просмотры"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Новость")
        verbose_name_plural = _("Новости")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"slug": self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=["views"])
