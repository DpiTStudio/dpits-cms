# services/models.py
from django.db import models
from django.db.models import F  # Атомарное обновление полей
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from main.models import HeroMixin


class ServiceCategory(HeroMixin):
    """Категория услуг"""

    name = models.CharField(_("Название"), max_length=100)
    slug = models.SlugField(_("URL"), unique=True)
    image = models.ImageField(
        _("Изображение"), upload_to="services/categories/", blank=True
    )
    description = CKEditor5Field(_("Описание"), blank=True, config_name="extends")

    # SEO поля
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)

    # Настройки отображения
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    order = models.IntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)
    views = models.PositiveIntegerField(_("Просмотры"), default=0)

    # Системные поля
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Категория услуг")
        verbose_name_plural = _("Категории услуг")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Создаем slug из названия, если он не задан."""
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            queryset = ServiceCategory.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f"{base_slug}-{counter}"
                queryset = ServiceCategory.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Возвращает абсолютный URL для просмотра категории."""
        return reverse("services:category", kwargs={"slug": self.slug})

    def services_count(self):
        """Количество услуг в категории"""
        return self.service_set.count()


class Service(HeroMixin):
    """Модель услуги"""

    PRICE_TYPE_CHOICES = (
        ("fixed", "Фиксированная цена"),
        ("from", "От"),
        ("to", "До"),
        ("range", "От и до"),
    )

    CURRENCY_CHOICES = (
        ("RUB", "Рубли (₽)"),
        ("USD", "Доллары ($)"),
        ("EUR", "Евро (€)"),
        ("KZT", "Тенге (₸)"),
    )

    # Основные поля
    name = models.CharField(_("Название услуги"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True, blank=True)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        verbose_name=_("Категория услуги"),
    )
    short_description = CKEditor5Field(
        _("Краткое описание услуги"), blank=True, config_name="extends"
    )
    description = CKEditor5Field(
        _("Описание услуги"), blank=True, config_name="extends"
    )

    # Изображения
    icon = models.ImageField(
        _("Иконка услуги"), upload_to="services/icons/", blank=True
    )
    background = models.ImageField(
        _("Фон услуги"), upload_to="services/backgrounds/", blank=True
    )

    # Цены
    price_type = models.CharField(
        _("Тип цены"),
        max_length=10,
        choices=PRICE_TYPE_CHOICES,
        default="fixed",
    )
    price_fixed = models.DecimalField(
        _("Фиксированная цена"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    price_from = models.DecimalField(
        _("Цена от"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    price_to = models.DecimalField(
        _("Цена до"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    currency = models.CharField(
        _("Валюта"),
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="RUB",
    )

    # Статусы
    can_order = models.BooleanField(
        _("Можно заказать"), default=True, help_text=_("Можно ли заказать эту услугу")
    )
    is_displayed = models.BooleanField(
        _("Отображается"),
        default=True,
        help_text=_("Будет ли отображаться услуга на сайте"),
    )

    # SEO поля
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)

    # Системные поля
    views = models.PositiveIntegerField(_("Просмотры"), default=0)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Создаем slug из названия, если он не задан."""
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            queryset = Service.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f"{base_slug}-{counter}"
                queryset = Service.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Возвращает абсолютный URL для просмотра услуги."""
        return reverse("services:detail", kwargs={"slug": self.slug})

    def get_price_display(self):
        """Возвращает отформатированную цену в зависимости от типа"""
        currency_symbols = {
            "RUB": "₽",
            "USD": "$",
            "EUR": "€",
            "KZT": "₸",
        }
        symbol = currency_symbols.get(self.currency, self.currency)

        if self.price_type == "fixed" and self.price_fixed:
            return f"{self.price_fixed:,.0f} {symbol}".replace(",", " ")
        elif self.price_type == "from" and self.price_from:
            return f"от {self.price_from:,.0f} {symbol}".replace(",", " ")
        elif self.price_type == "to" and self.price_to:
            return f"до {self.price_to:,.0f} {symbol}".replace(",", " ")
        elif self.price_type == "range" and self.price_from and self.price_to:
            return f"{self.price_from:,.0f} - {self.price_to:,.0f} {symbol}".replace(
                ",", " "
            )
        return _("Цена по запросу")

    def increment_views(self):
        """
        Атомарно увеличивает счётчик просмотров на 1.
        Использует F() для защиты от race condition при одновременных запросах.
        """
        Service.objects.filter(pk=self.pk).update(views=F("views") + 1)
        self.refresh_from_db(fields=["views"])
