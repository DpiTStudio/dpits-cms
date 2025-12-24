# portfolio/models.py
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import format_html  # Добавлен импорт
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
    description = CKEditor5Field(_("Описание"), blank=True, config_name="extends")
    is_verified = models.BooleanField(_("Подтвержден"), default=False)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)

    class Meta:
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_absolute_url(self):
        return reverse("portfolio:client_profile")


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

    # SEO поля
    seo_title = models.CharField(
        _("SEO заголовок"), max_length=200, blank=True, default=""
    )
    seo_description = models.CharField(
        _("SEO описание"), max_length=200, blank=True, default=""
    )
    seo_keywords = models.CharField(
        _("SEO ключевые слова"), max_length=200, blank=True, default=""
    )

    # Порядок отображения
    order = models.IntegerField(
        _("Порядок"), default=0, help_text=_("Чем больше, тем выше")
    )
    is_active = models.BooleanField(_("Активно"), default=True)

    # Системные поля
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)

    class Meta:
        verbose_name = _("Категория портфолио")
        verbose_name_plural = _("Категории портфолио")
        ordering = ["-order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Создаем slug из названия, если он не задан.
        ИСПРАВЛЕНО: Добавлена проверка уникальности slug с исключением текущего объекта.
        """
        if not self.slug:
            base_slug = slugify(self.name)  # Преобразуем название в slug
            self.slug = base_slug  # Устанавливаем базовый slug
            # Убеждаемся, что slug уникален (исключаем текущий объект при обновлении)
            counter = 1
            # ИСПРАВЛЕНО: Добавлен фильтр для исключения текущего объекта при проверке уникальности
            queryset = PortfolioCategory.objects.filter(slug=self.slug)
            if self.pk:  # Если объект уже существует (обновление)
                queryset = queryset.exclude(pk=self.pk)  # Исключаем текущий объект
            while queryset.exists():  # Пока slug не уникален
                self.slug = f"{base_slug}-{counter}"  # Добавляем номер к slug
                queryset = PortfolioCategory.objects.filter(slug=self.slug)
                if self.pk:  # Если объект уже существует
                    queryset = queryset.exclude(pk=self.pk)  # Исключаем текущий объект
                counter += 1  # Увеличиваем счетчик
        super().save(*args, **kwargs)  # Вызываем метод save родительского класса

    def get_absolute_url(self):
        return reverse("portfolio:list") + f"?category={self.slug}"

    def works_count(self):
        """Количество работ в категории"""
        return self.portfolioitem_set.count()


class PortfolioItem(models.Model):
    """Элемент портфолио"""

    STATUS_CHOICES = (
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("archived", "В архиве"),
    )

    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True, blank=True)
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
    image = models.ImageField(
        _("Главное изображение"),
        upload_to=custom_upload_to,
        default="portfolio/default-category.png",
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
        """
        Автоматически генерирует уникальный slug и создает новость при публикации.
        """
        # Генерация slug
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            queryset = PortfolioItem.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f"{base_slug}-{counter}"
                queryset = PortfolioItem.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                counter += 1

        # Сохранение объекта
        super().save(*args, **kwargs)

        # Создание новости при публикации
        if self.status == "published":
            self.create_news_from_portfolio()

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})

    def get_technologies_list(self):
        """Возвращает список технологий, разделённых запятыми."""
        return (
            [tech.strip() for tech in self.technologies.split(",")]
            if self.technologies
            else []
        )

    def increment_views(self):
        """Увеличивает счётчик просмотров без полной перезаписи объекта."""
        self.views += 1
        self.save(update_fields=["views"])

    def create_news_from_portfolio(self):
        """
        Создаёт новость на основе элемента портфолио, если она ещё не создана.
        """
        from news.models import News, NewsCategory

        # Проверка статуса
        if self.status != "published":
            return

        # Проверка существования новости
        if News.objects.filter(slug=f"portfolio-{self.slug}").exists():
            return

        # Получение или создание категории "Портфолио"
        portfolio_category, _ = NewsCategory.objects.get_or_create(
            slug="portfolio",
            defaults={
                "name": "Портфолио",
                "description": "Новости о новых работах в портфолио",
                "show_in_menu": True,
                "order": 10,
                "is_active": True,
            },
        )

        # Создание новости
        News.objects.create(
            title=f"Добавлена новая работа: {self.title}",
            slug=f"portfolio-{self.slug}",
            category=portfolio_category,
            image=self.image,
            short_description=self.short_description,
            content=self.create_news_content(),
            is_active=True,
        )

    def create_news_content(self):
        """
        Генерирует HTML-контент для новости на основе данных портфолио.
        """
        client_html = (
            f"<p><strong>Клиент:</strong> {self.client}</p>" if self.client else ""
        )
        technologies_html = (
            f"<p><strong>Технологии:</strong> {self.technologies}</p>"
            if self.technologies
            else ""
        )
        project_url_html = (
            f'<p><strong>Ссылка на проект:</strong> <a href="{self.project_url}" target="_blank">{self.project_url}</a></p>'
            if self.project_url
            else ""
        )
        github_url_html = (
            f'<p><strong>GitHub:</strong> <a href="{self.github_url}" target="_blank">{self.github_url}</a></p>'
            if self.github_url
            else ""
        )

        return f"""
        <div class="portfolio-news">
            <h2>{self.title}</h2>
            <div class="portfolio-info">
                <p><strong>Категория:</strong> {self.category.name}</p>
                <p><strong>Дата проекта:</strong> {self.project_date}</p>
                {client_html}
                {technologies_html}
                {project_url_html}
                {github_url_html}
            </div>
            <div class="portfolio-description">
                <h3>Описание работы</h3>
                {self.content}
            </div>
            <div class="portfolio-actions mt-4">
                <a href="{self.get_absolute_url()}" class="btn btn-primary">
                    <i class="fas fa-external-link-alt"></i> Посмотреть детали работы
                </a>
            </div>
        </div>
        """

        """
        Генерирует HTML-контент для новости.
        """
        content = f"""
        <div class="portfolio-news">
            <h2>{self.title}</h2>
            
            <div class="portfolio-info">
                <p><strong>Категория:</strong> {self.category.name}</p>
                <p><strong>Дата проекта:</strong> {self.project_date}</p>
                
                {f"<p><strong>Клиент:</strong> {self.client}</p>" if self.client else ""}
                
                {f"<p><strong>Технологии:</strong> {self.technologies}</p>" if self.technologies else ""}
                
                {f'<p><strong>Ссылка на проект:</strong> <a href="{self.project_url}" target="_blank">{self.project_url}</a></p>' if self.project_url else ""}
                
                {f'<p><strong>GitHub:</strong> <a href="{self.github_url}" target="_blank">{self.github_url}</a></p>' if self.github_url else ""}
            </div>
            
            <div class="portfolio-description">
                <h3>Описание работы</h3>
                {self.content}
            </div>
            
            <div class="portfolio-actions mt-4">
                <a href="{self.get_absolute_url()}" class="btn btn-primary">
                    <i class="fas fa-external-link-alt"></i> Посмотреть детали работы
                </a>
            </div>
        </div>
        """

        return content


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

    @property
    def is_overdue(self):
        """Проверяет, просрочен ли заказ"""
        from django.utils import timezone

        return self.deadline and self.deadline < timezone.now().date()

    def get_progress_percentage(self):
        """Возвращает процент выполнения заказа"""
        status_progress = {
            "new": 25,
            "in_progress": 50,
            "completed": 100,
            "cancelled": 0,
        }
        return status_progress.get(self.status, 0)


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

    is_admin_message = models.BooleanField(_("Сообщение администратора"), default=False)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)

    class Meta:
        verbose_name = _("Сообщение заказа")
        verbose_name_plural = _("Сообщения заказов")
        ordering = ["created_at"]

    def __str__(self):
        return f"Сообщение для заказа #{self.order.id}"

    def save(self, *args, **kwargs):
        """Автоматически помечает сообщения от админов"""
        if self.user.is_staff:
            self.is_admin_message = True
        super().save(*args, **kwargs)


class PortfolioReview(models.Model):
    """Отзывы клиентов о работах портфолио"""

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
        verbose_name = _("Отзыв о работе")
        verbose_name_plural = _("Отзывы о работах")
        ordering = ["-created_at"]
        unique_together = ["client", "portfolio_item"]

    def __str__(self):
        return f"Отзыв от {self.client} - {self.portfolio_item.title}"

    def get_star_rating(self):
        """Возвращает HTML для отображения звезд рейтинга"""
        stars = ""
        for i in range(1, 6):
            if i <= self.rating:
                stars += '<i class="fas fa-star text-warning"></i>'
            else:
                stars += '<i class="far fa-star text-muted"></i>'
        return format_html(stars)
