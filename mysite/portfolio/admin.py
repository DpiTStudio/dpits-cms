# ============================================================================================= #
# ФАЙЛ: ADMIN.PY                                                                                #
# ОПИСАНИЕ:                                                                                     #
# Настройки интерфейса администратора Django для приложения Портфолио. Определяет, как модели   #
# отображаются, редактируются и фильтруются в панели управления.                                #
#                                                                                               #
# НЮАНСЫ И ФУНКЦИОНАЛ:                                                                          #
# 1. Кастомизация списков (list_display):                                                       #
#    - Добавлены превью изображений (image_preview).                                            #
#    - Вычисляемые поля (количество работ в категории).                                         #
#    - Цветовая индикация и форматирование (звезды рейтинга для отзывов).                       #
# 2. Формы редактирования:                                                                      #
#    - Использование fieldsets для группировки полей (SEO, Основное, Настройки Hero).           #
#    - Сворачиваемые блоки (collapse) для второстепенной информации.                            #
# 3. Действия (Actions):                                                                        #
#    - Массовая модерация отзывов (Одобрить/Отклонить).                                         #
#    - "Создать новости из выбранных работ" - кастомное действие для автоматизации контента.    #
# 4. Удобство:                                                                                  #
#    - Фильтры (list_filter) и поиск (search_fields) по всем ключевым параметрам.               #
#    - readonly_fields для защиты системных данных (даты создания, просмотры).                  #
# ============================================================================================= #
# portfolio/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    PortfolioCategory,
    PortfolioItem,
    Client,
    Order,
    OrderMessage,
    PortfolioReview,
)


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий портфолио"""
    # Поля для отображения в списке
    list_display = (
        "name",
        "slug",
        "order",
        "is_active",
        "works_count",
        "created_at",
    )
    # Фильтры для боковой панели
    list_filter = ["is_active", "created_at"]
    # Поля для поиска
    search_fields = ["name", "description"]
    # Автозаполнение slug из name
    prepopulated_fields = {"slug": ("name",)}
    # Только для чтения поля
    readonly_fields = ["created_at", "updated_at", "works_count_display"]
    # Список редактируемых полей прямо из списка
    list_editable = ["order", "is_active"]
    # Элементов на странице
    list_per_page = 20

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            # Заголовок группы полей
            _("Основная информация"),
            # Поля в группе
            {"fields": ("name", "slug", "description", "order", "is_active")},
        ),
        (
            _("Настройки Hero-секции"),
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                    "hero_image",
                    "hero_is_active",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            # Заголовок группы полей
            _("SEO настройки"),
            # Поля в группе
            {"fields": ("seo_title", "seo_description", "seo_keywords")},
        ),
        (
            # Заголовок группы полей
            _("Статистика"),
            # Поля в группе
            {"fields": ("created_at", "updated_at", "works_count_display")},
        ),
    )

    def works_count(self, obj):
        """Количество работ в категории"""
        return obj.portfolioitem_set.count()

    works_count.short_description = _("Количество работ")

    def works_count_display(self, obj):
        """Отображение количества работ в форме редактирования"""
        return obj.works_count()

    works_count_display.short_description = _("Количество работ")


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    """Админ-панель для работ портфолио"""

    # Поля для отображения в списке
    list_display = [
        "title",
        "category",
        "status",
        "project_date",
        "views",
        "created_at",
        "image_preview",
    ]
    # Фильтры для боковой панели
    list_filter = ["status", "category", "project_date", "created_at"]
    # Поля для поиска
    search_fields = ["title", "short_description", "content", "technologies"]
    # Автозаполнение slug из title
    prepopulated_fields = {"slug": ("title",)}
    # Только для чтения поля
    readonly_fields = ["views", "created_at", "updated_at", "image_preview_large"]
    # Иерархия по дате проекта
    date_hierarchy = "project_date"
    # Список редактируемых полей
    list_editable = ["status"]
    # Элементов на странице
    list_per_page = 20

    def image_preview(self, obj):
        """Превью изображения в списке"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url,
            )
        return _("Нет изображения")

    image_preview.short_description = _("Превью")

    def image_preview_large(self, obj):
        """Большое превью изображения в форме редактирования"""
        if obj.image:
            return format_html(
                '<img src="{}" width="200" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url,
            )
        return _("Нет изображения")

    image_preview_large.short_description = _("Превью изображения")

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("title", "slug", "category", "client", "status")},
        ),
        (
            _("Медиа-контент"),
            {
                "fields": (
                    "image",
                    "image_preview_large",
                    "short_description",
                    "content",
                )
            },
        ),
        (
            _("Технические детали"),
            {
                "fields": ("technologies", "project_date", "project_url", "github_url"),
                "classes": ("collapse",),
            },
        ),
        (
            _("SEO настройки"),
            {
                "fields": ("seo_title", "seo_description", "seo_keywords"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Настройки Hero-секции"),
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                    "hero_image",
                    "hero_is_active",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Статистика"),
            {"fields": ("views", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["create_news_from_portfolio"]

    def create_news_from_portfolio(self, request, queryset):
        """
        Действие для создания новостей из выбранных работ портфолио.
        """
        from news.models import News, NewsCategory

        # Находим или создаем категорию
        portfolio_category, _ = NewsCategory.objects.get_or_create(
            name="Портфолио",
            defaults={
                "slug": "portfolio",
                "description": "Новости о новых работах в портфолио",
                "show_in_menu": True,
                "order": 10,
                "is_active": True,
            },
        )

        created_count = 0
        for portfolio_item in queryset:
            # Проверяем, не существует ли уже новость
            if not News.objects.filter(
                slug=f"portfolio-{portfolio_item.slug}"
            ).exists():
                News.objects.create(
                    title=f"Новая работа: {portfolio_item.title}",
                    slug=f"portfolio-{portfolio_item.slug}",
                    category=portfolio_category,
                    image=portfolio_item.image,
                    short_description=portfolio_item.short_description[:200],
                    content=portfolio_item.create_news_content(),
                    is_active=True,
                )
                created_count += 1

        self.message_user(
            request, f"Создано {created_count} новостей из выбранных работ портфолио."
        )

    create_news_from_portfolio.short_description = "Создать новости из выбранных работ"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Админ-панель для клиентов"""

    # Поля для отображения в списке
    list_display = ["user", "company", "is_verified", "created_at", "user_email"]
    # Фильтры для боковой панели
    list_filter = ["is_verified", "created_at"]
    # Поля для поиска
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "company",
    ]
    # Только для чтения поля
    readonly_fields = ["created_at", "updated_at", "user_email_display"]
    # Список редактируемых полей
    list_editable = ["is_verified"]
    # Элементов на странице
    list_per_page = 20

    def user_email(self, obj):
        """Email пользователя в списке"""
        return obj.user.email

    user_email.short_description = _("Email")

    def user_email_display(self, obj):
        """Email пользователя в форме редактирования"""
        return obj.user.email

    user_email_display.short_description = _("Email")

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("user", "user_email_display", "company", "phone", "website")},
        ),
        (_("Описание"), {"fields": ("description",)}),
        (_("Статус"), {"fields": ("is_verified",)}),
        (_("Даты"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админ-панель для заказов"""

    # Поля для отображения в списке
    list_display = [
        "id",
        "client",
        "title",
        "status",
        "priority",
        "budget",
        "created_at",
        "is_overdue",
    ]
    # Фильтры для боковой панели
    list_filter = ["status", "priority", "created_at"]
    # Поля для поиска
    search_fields = [
        "title",
        "description",
        "client__user__username",
        "client__company",
    ]
    # Только для чтения поля
    readonly_fields = ["created_at", "updated_at", "is_overdue_display"]
    # Список редактируемых полей
    list_editable = ["status", "priority"]
    # Элементов на странице
    list_per_page = 20

    def is_overdue(self, obj):
        """Отображение просроченных заказов в списке"""
        return obj.is_overdue

    is_overdue.short_description = _("Просрочен")
    is_overdue.boolean = True

    def is_overdue_display(self, obj):
        """Отображение статуса просрочки в форме"""
        return _("Да") if obj.is_overdue else _("Нет")

    is_overdue_display.short_description = _("Просрочен")

    # Группировка полей в форме редактирования
    fieldsets = (
        (_("Основная информация"), {"fields": ("client", "title", "description")}),
        (
            _("Финансы и сроки"),
            {"fields": ("budget", "deadline", "is_overdue_display")},
        ),
        (_("Статус и приоритет"), {"fields": ("status", "priority")}),
        (
            _("Дополнительные файлы"),
            {
                "fields": ("requirements_file", "additional_notes"),
                "classes": ("collapse",),
            },
        ),
        (_("Даты"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(OrderMessage)
class OrderMessageAdmin(admin.ModelAdmin):
    """Админ-панель для сообщений заказов"""

    # Поля для отображения в списке
    list_display = [
        "id",
        "order",
        "user",
        "is_admin_message",
        "created_at",
        "message_preview",
    ]
    # Фильтры для боковой панели
    list_filter = ["is_admin_message", "created_at"]
    # Поля для поиска
    search_fields = ["message", "order__title", "user__username"]
    # Только для чтения поля
    readonly_fields = ["created_at"]
    # Элементов на странице
    list_per_page = 20

    def message_preview(self, obj):
        """Краткий предпросмотр сообщения"""
        preview = obj.message[:50]
        if len(obj.message) > 50:
            preview += "..."
        return preview

    message_preview.short_description = _("Предпросмотр сообщения")

    # Группировка полей в форме редактирования
    fieldsets = (
        (_("Основная информация"), {"fields": ("order", "user", "is_admin_message")}),
        (_("Сообщение"), {"fields": ("message", "file")}),
        (_("Дата"), {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(PortfolioReview)
class PortfolioReviewAdmin(admin.ModelAdmin):
    """Админ-панель для отзывов о работах"""

    # Поля для отображения в списке
    list_display = [
        "portfolio_item",
        "client",
        "rating",
        "title",
        "is_approved",
        "created_at",
        "rating_stars",
    ]
    # Фильтры для боковой панели
    list_filter = ["rating", "is_approved", "created_at"]
    # Поля для поиска
    search_fields = [
        "title",
        "content",
        "client__user__username",
        "portfolio_item__title",
    ]
    # Только для чтения поля
    readonly_fields = ["created_at", "rating_stars_display"]
    # Список редактируемых полей
    list_editable = ["is_approved"]
    # Элементов на странице
    list_per_page = 20

    def rating_stars(self, obj):
        """Отображение рейтинга звездами в списке"""
        return format_html(obj.get_star_rating())

    rating_stars.short_description = _("Рейтинг")

    def rating_stars_display(self, obj):
        """Отображение рейтинга звездами в форме"""
        return format_html(obj.get_star_rating())

    rating_stars_display.short_description = _("Рейтинг")

    # Группировка полей в форме редактирования
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("portfolio_item", "client", "rating", "rating_stars_display")},
        ),
        (_("Содержание отзыва"), {"fields": ("title", "content")}),
        (_("Модерация"), {"fields": ("is_approved",)}),
        (_("Дата"), {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    # Действия для массовой модерации
    actions = ["approve_reviews", "disapprove_reviews"]

    def approve_reviews(self, request, queryset):
        """Массовое одобрение отзывов"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} отзывов одобрено.")

    approve_reviews.short_description = _("Одобрить выбранные отзывы")

    def disapprove_reviews(self, request, queryset):
        """Массовое отклонение отзывов"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} отзывов отклонено.")

    disapprove_reviews.short_description = _("Отклонить выбранные отзывы")
