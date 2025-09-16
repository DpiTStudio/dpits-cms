# portfolio/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class PortfolioCategory(models.Model):
    name = models.CharField(_("Название"), max_length=100)
    slug = models.SlugField(_("URL"), unique=True)
    image = models.ImageField(
        _("Изображение"), upload_to="portfolio/categories/", blank=True
    )
    description = models.TextField(_("Описание"), blank=True)
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    order = models.IntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)

    class Meta:
        verbose_name = _("Категория портфолио")
        verbose_name_plural = _("Категории портфолио")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:category", kwargs={"slug": self.slug})


class Portfolio(models.Model):
    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True)
    category = models.ForeignKey(
        PortfolioCategory, on_delete=models.CASCADE, verbose_name=_("Категория")
    )
    image = models.ImageField(_("Изображение"), upload_to="portfolio/")
    short_description = models.TextField(_("Краткое описание"))
    content = CKEditor5Field(_("Содержание"), blank=True, config_name="extends")
    price = models.DecimalField(
        _("Цена"), max_digits=10, decimal_places=2, blank=True, null=True
    )
    can_order = models.BooleanField(_("Можно заказать"), default=True)
    views = models.PositiveIntegerField(_("Просмотры"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Работа портфолио")
        verbose_name_plural = _("Работы портфолио")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=["views"])
