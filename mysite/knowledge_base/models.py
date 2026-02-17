from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings

class Category(models.Model):
    """
    Категория базы знаний.
    """
    name = models.CharField(_("Название"), max_length=100)
    slug = models.SlugField(_("URL"), unique=True, max_length=100)
    description = models.TextField(_("Описание"), blank=True)
    icon = models.CharField(
        _("Иконка (FontAwesome)"), 
        max_length=50, 
        default="fas fa-folder",
        help_text=_("Например: fas fa-book")
    )
    order = models.IntegerField(_("Порядок сортировки"), default=0)
    
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Категория знаний")
        verbose_name_plural = _("Категории знаний")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("knowledge_base:category_detail", kwargs={"slug": self.slug})


class Article(models.Model):
    """
    Статья базы знаний.
    """
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="articles",
        verbose_name=_("Категория")
    )
    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True, max_length=200)
    content = CKEditor5Field(_("Содержание"), config_name="extends")
    
    is_published = models.BooleanField(_("Опубликовано"), default=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Автор")
    )
    
    # Статистика
    views_count = models.PositiveIntegerField(_("Просмотры"), default=0)
    helpful_count = models.PositiveIntegerField(_("Полезно"), default=0)
    not_helpful_count = models.PositiveIntegerField(_("Не полезно"), default=0)
    
    # SEO
    seo_title = models.CharField(_("SEO Title"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO Description"), max_length=255, blank=True)
    seo_keywords = models.CharField(_("SEO Keywords"), max_length=200, blank=True)
    
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Статья")
        verbose_name_plural = _("Статьи")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("knowledge_base:article_detail", kwargs={"slug": self.slug})
