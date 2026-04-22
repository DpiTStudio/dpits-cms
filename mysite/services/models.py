# services/models.py
# Назначение: Модели данных приложения "Услуги".
# Категории услуг, услуги, заказы и позиции заказов.

from django.db import models
from django.db.models import F  # Для атомарного обновления полей (без race condition)
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from main.models import HeroMixin  # Примесь для Hero-секции (заголовок, подзаголовок, изображение)


class ServiceCategory(HeroMixin):
    """
    Категория услуг.
    Например: "Веб-разработка", "SEO-продвижение", "Дизайн".
    """
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", unique=True)  # Используется в адресе страницы
    image = models.ImageField("Изображение", upload_to="services/categories/", blank=True)
    description = CKEditor5Field("Описание", blank=True, config_name="extends")  # RichText редактор

    # SEO-поля для продвижения в поисковых системах
    seo_title = models.CharField("SEO заголовок", max_length=200, blank=True)
    seo_keywords = models.CharField("SEO ключевые слова", max_length=200, blank=True)
    seo_description = models.CharField("SEO описание", max_length=255, blank=True)

    # Настройки отображения
    show_in_menu = models.BooleanField("Показывать в меню", default=True)
    order = models.IntegerField("Порядок", default=0)  # Для сортировки категорий
    is_active = models.BooleanField("Активно", default=True)  # Скрыть/показать категорию
    views = models.PositiveIntegerField("Просмотры", default=0)

    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        ordering = ["order", "name"]  # Сортировка по порядку, затем по имени

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Переопределённый метод save.
        Автоматически генерирует уникальный slug из названия, если slug не задан.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            # Проверяем уникальность slug
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
        """
        Возвращает URL для просмотра категории на сайте.
        """
        return reverse("services:category", kwargs={"slug": self.slug})

    def services_count(self):
        """
        Возвращает количество услуг в данной категории.
        """
        return self.service_set.count()


class Service(HeroMixin):
    """
    Модель услуги.
    Содержит информацию о конкретной услуге: цену, описание, изображения.
    """
    # Типы цен (выбор из кортежа)
    PRICE_TYPE_CHOICES = (
        ("fixed", "Фиксированная цена"),
        ("from", "От"),
        ("to", "До"),
        ("range", "От и до"),
    )

    # Валюты
    CURRENCY_CHOICES = (
        ("RUB", "Рубли (₽)"),
        ("USD", "Доллары ($)"),
        ("EUR", "Евро (€)"),
        ("KZT", "Тенге (₸)"),
    )

    # Основные поля
    name = models.CharField("Название услуги", max_length=200)
    slug = models.SlugField("URL", unique=True, blank=True)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,  # При удалении категории удаляются все услуги в ней
        verbose_name="Категория услуги",
    )
    short_description = CKEditor5Field("Краткое описание услуги", blank=True, config_name="extends")
    description = CKEditor5Field("Описание услуги", blank=True, config_name="extends")

    # Изображения
    icon = models.ImageField("Иконка услуги", upload_to="services/icons/", blank=True)
    background = models.ImageField("Фон услуги", upload_to="services/backgrounds/", blank=True)

    # Цены
    price_type = models.CharField("Тип цены", max_length=10, choices=PRICE_TYPE_CHOICES, default="fixed")
    price_fixed = models.DecimalField("Фиксированная цена", max_digits=10, decimal_places=2, null=True, blank=True)
    price_from = models.DecimalField("Цена от", max_digits=10, decimal_places=2, null=True, blank=True)
    price_to = models.DecimalField("Цена до", max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField("Валюта", max_length=3, choices=CURRENCY_CHOICES, default="RUB")

    # Статусы
    can_order = models.BooleanField("Можно заказать", default=True, help_text="Можно ли заказать эту услугу")
    is_displayed = models.BooleanField("Отображается", default=True, help_text="Будет ли отображаться услуга на сайте")

    # SEO
    seo_title = models.CharField("SEO заголовок", max_length=200, blank=True)
    seo_keywords = models.CharField("SEO ключевые слова", max_length=200, blank=True)
    seo_description = models.CharField("SEO описание", max_length=255, blank=True)

    # Системные поля
    views = models.PositiveIntegerField("Просмотры", default=0)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["-created_at"]  # Новые услуги вверху

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Генерация уникального slug из названия.
        """
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
        """
        URL для просмотра детальной страницы услуги.
        """
        return reverse("services:detail", kwargs={"slug": self.slug})

    def get_price_display(self):
        """
        Форматирует цену для отображения на сайте.
        Учитывает тип цены (фикс, от, до, диапазон) и валюту.
        ИСПРАВЛЕНО: добавлена обработка случая, когда все цены None.
        """
        currency_symbols = {
            "RUB": "₽",
            "USD": "$",
            "EUR": "€",
            "KZT": "₸",
        }
        symbol = currency_symbols.get(self.currency, self.currency)

        # Проверяем наличие цен в зависимости от типа
        if self.price_type == "fixed" and self.price_fixed is not None:
            return f"{self.price_fixed:,.0f} {symbol}".replace(",", " ")
        elif self.price_type == "from" and self.price_from is not None:
            return f"от {self.price_from:,.0f} {symbol}".replace(",", " ")
        elif self.price_type == "to" and self.price_to is not None:
            return f"до {self.price_to:,.0f} {symbol}".replace(",", " ")
        elif self.price_type == "range" and self.price_from is not None and self.price_to is not None:
            return f"{self.price_from:,.0f} - {self.price_to:,.0f} {symbol}".replace(",", " ")
        return "Цена по запросу"

    def increment_views(self):
        """
        Увеличивает счётчик просмотров на 1.
        Использует F() для атомарного обновления (безопасно при параллельных запросах).
        """
        Service.objects.filter(pk=self.pk).update(views=F("views") + 1)
        self.refresh_from_db(fields=["views"])  # Обновляем текущий объект


class ServiceOrder(models.Model):
    """
    Заказ услуг, созданный из корзины.
    Поддерживает гостевые заказы (user может быть null) и авторизованных пользователей.
    """
    STATUS_CHOICES = (
        ("new", "Новый"),
        ("in_progress", "В работе"),
        ("completed", "Выполнен"),
        ("cancelled", "Отменён"),
    )

    ORDER_TYPE_CHOICES = (
        ("quick", "Быстрый"),
        ("full", "Полный"),
    )

    # Пользователь (может быть null для гостевых заказов)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # При удалении пользователя заказ остаётся, user = null
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name="service_orders",
    )

    # Контактные данные клиента (дублируем, чтобы сохранить даже если пользователь удалён)
    client_name = models.CharField("Имя клиента", max_length=150)
    client_email = models.EmailField("Email клиента")
    client_phone = models.CharField("Телефон клиента", max_length=30, blank=True)

    # Детали заказа
    comment = models.TextField("Комментарий", blank=True)
    order_type = models.CharField("Тип заказа", max_length=10, choices=ORDER_TYPE_CHOICES, default="quick")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")

    # Финансы
    total_price = models.DecimalField("Итого", max_digits=12, decimal_places=2, default=0)

    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} — {self.client_name}"

    def get_absolute_url(self):
        return reverse("services:order_detail", kwargs={"pk": self.pk})


class ServiceOrderItem(models.Model):
    """
    Позиция заказа (одна услуга в заказе).
    Сохраняет название, цену и количество на момент заказа (даже если услуга потом изменится).
    """
    order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,  # При удалении заказа удаляются все его позиции
        verbose_name="Заказ",
        related_name="items",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,  # При удалении услуги из БД позиция остаётся с service = null
        null=True,
        blank=True,
        verbose_name="Услуга",
        related_name="order_items",
    )
    service_name = models.CharField("Название услуги", max_length=255)  # Дублируем название
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.service_name} × {self.quantity}"

    @property
    def total_price(self):
        """
        Сумма по позиции (цена × количество).
        """
        return self.price * self.quantity