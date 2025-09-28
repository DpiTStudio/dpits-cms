# portfolio/models.py
import datetime
from email.mime import image
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from .utils import custom_upload_to


class Client(models.Model):
    """Модель клиента/заказчика"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    company = models.CharField(_("Компания"), max_length=200, blank=True)
    phone = models.CharField(_("Телефон"), max_length=20, blank=True)
    website = models.URLField(_("Веб-сайт"), blank=True)
    description = CKEditor5Field(_("Описание"), blank=False, config_name="extends")
    is_verified = models.BooleanField(_("Подтвержден"), default=False)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class PortfolioCategory(models.Model):
    """Категории портфолио"""

    name = models.CharField(_("Название"), max_length=100)
    image = models.ImageField(
        _("Изображение"),
        upload_to=custom_upload_to,
        default="portfolio/default-category.png",
    )
    slug = models.SlugField(_("URL"), unique=True)
    description = CKEditor5Field(_("Описание"), blank=True, config_name="extends")
    # SEO
    seo_title = models.CharField(
        _("SEO заголовок"), max_length=200, blank=True, default=""
    )
    seo_description = models.CharField(
        _("SEO описание"), max_length=200, blank=True, default=""
    )
    seo_keywords = models.CharField(
        _("SEO ключевые слова"), max_length=200, blank=True, default=""
    )

    # Порядок
    order = models.IntegerField(
        _("Порядок"), default=0, help_text=_("Чем больше, тем выше")
    )

    # Системные поля
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)
    # Публикация
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


class PortfolioItem(models.Model):
    """Элемент портфолио"""

    STATUS_CHOICES = (
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("archived", "В архиве"),
    )

    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True)
    category = models.ForeignKey(
        PortfolioCategory, on_delete=models.CASCADE, verbose_name=_("Категория")
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Клиент"),
    )
    images = models.ImageField(
        _("Главное изображение"),
        upload_to=custom_upload_to,
    )
    short_description = models.TextField(_("Краткое описание"), max_length=300)
    content = CKEditor5Field(_("Содержание"), config_name="extends")

    # Технические детали
    technologies = models.CharField(
        _("Технологии"), max_length=300, blank=True, help_text=_("Через запятую")
    )
    project_date = models.DateField(
        _("Дата проекта"), null=True, blank=True, default=datetime.date.today
    )
    project_url = models.URLField(_("Ссылка на проект"), blank=True)
    github_url = models.URLField(_("Ссылка на GitHub"), blank=True)

    # Статус и SEO
    status = models.CharField(
        _("Статус"), max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=300, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)

    # Системные поля
    views = models.PositiveIntegerField(_("Просмотры"), default=0)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)

    class Meta:
        verbose_name = _("Работа портфолио")
        verbose_name_plural = _("Работы портфолио")
        ordering = ["-project_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})


class Order(models.Model):
    """Модель заказа"""

    STATUS_CHOICES = (
        ("new", "Новый"),
        ("in_progress", "В работе"),
        ("completed", "Завершен"),
        ("cancelled", "Отменен"),
    )

    PRIORITY_CHOICES = (
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
        ("urgent", "Срочный"),
    )

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name=_("Клиент")
    )
    title = models.CharField(_("Название проекта"), max_length=200)
    description = models.TextField(_("Описание проекта"))
    budget = models.DecimalField(
        _("Бюджет"), max_digits=10, decimal_places=2, null=True, blank=True
    )
    deadline = models.DateField(_("Срок выполнения"), null=True, blank=True)

    # Статус и приоритет
    status = models.CharField(
        _("Статус"), max_length=20, choices=STATUS_CHOICES, default="new"
    )
    priority = models.CharField(
        _("Приоритет"), max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )

    # Файлы и доп. информация
    requirements_file = models.FileField(
        _("Файл требований"), upload_to=custom_upload_to, blank=True
    )
    additional_notes = models.TextField(_("Дополнительные заметки"), blank=True)

    # Системные поля
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} - {self.title}"

    def get_absolute_url(self):
        return reverse("portfolio:order_detail", kwargs={"pk": self.pk})


class OrderMessage(models.Model):
    """Сообщения в заказе"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("Заказ"),
        related_name="messages",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    message = models.TextField(_("Сообщение"))
    file = models.FileField(
        _("Файл"),
        upload_to=custom_upload_to,
        blank=True,
    )
    #
    is_admin_message = models.BooleanField(_("Сообщение администратора"), default=False)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)

    class Meta:
        verbose_name = _("Сообщение заказа")
        verbose_name_plural = _("Сообщения заказов")
        ordering = ["created_at"]

    def __str__(self):
        return f"Сообщение для заказа #{self.order.id}"


class Review(models.Model):
    """Отзывы клиентов"""

    RATING_CHOICES = (
        (1, "1 - Ужасно"),
        (2, "2 - Плохо"),
        (3, "3 - Нормально"),
        (4, "4 - Хорошо"),
        (5, "5 - Отлично"),
    )

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name=_("Клиент")
    )
    portfolio_item = models.ForeignKey(
        PortfolioItem, on_delete=models.CASCADE, verbose_name=_("Работа")
    )
    rating = models.IntegerField(_("Рейтинг"), choices=RATING_CHOICES)
    title = models.CharField(_("Заголовок отзыва"), max_length=200)
    content = models.TextField(_("Текст отзыва"))
    is_approved = models.BooleanField(_("Одобрено"), default=False)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.client} - {self.portfolio_item.title}"
