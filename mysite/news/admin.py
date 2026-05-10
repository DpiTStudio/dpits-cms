from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from main.admin_utils import ResetAutoIncrementMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone
from .models import NewsCategory, News, NewsTag


@admin.register(NewsTag)
class NewsTagAdmin(ResetAutoIncrementMixin, admin.ModelAdmin):
    """Управление тегами новостей."""
    list_display = ["name", "slug", "news_count_display"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def news_count_display(self, obj):
        count = obj.news.filter(is_active=True).count()
        return format_html(
            '<span style="font-weight:bold;color:#6366f1">{}</span> новостей', count
        )
    news_count_display.short_description = "Новостей"


@admin.register(NewsCategory)
class NewsCategoryAdmin(ResetAutoIncrementMixin, admin.ModelAdmin):
    """
    Админ-панель для управления категориями новостей.
    Поддержка SEO, сортировки, отображения в меню и управления активностью.
    """

    list_display = ["name", "slug", "news_count_display", "show_in_menu", "order", "is_active", "views"]
    list_editable = ["show_in_menu", "order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "slug"]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "image", "description")}),
        ("Настройки отображения", {"fields": ("show_in_menu", "order", "is_active")}),
        (
            "Настройки Hero-секции",
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
            "SEO оптимизация",
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "Просмотры",
            {
                "fields": ("views",),
                "classes": ("collapse",),
            },
        ),
    )

    def news_count_display(self, obj):
        count = obj.news_set.filter(is_active=True).count()
        return format_html(
            '<span style="font-weight:bold;color:#6366f1">{}</span>', count
        )
    news_count_display.short_description = "Новостей"


@admin.register(News)
class NewsAdmin(ResetAutoIncrementMixin, admin.ModelAdmin):
    """
    Админ-панель для управления новостями.
    Поддержка фильтрации, SEO, сброса просмотров (массово и для отдельных записей),
    дублирования новости и управления статусом публикации.
    """

    list_display = [
        "title",
        "category",
        "status_display",
        "views",
        "reading_time_display",
        "is_active",
        "published_at",
        "created_at",
        "clear_views_button",
    ]
    list_filter = ["category", "is_active", "published_at", "created_at", "tags"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["views", "created_at", "updated_at", "reading_time_display"]
    filter_horizontal = ["tags"]
    search_fields = ["title", "slug", "short_description"]
    date_hierarchy = "published_at"

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "image",
                    "tags",
                    "short_description",
                    "content",
                )
            },
        ),
        (
            "Статистика",
            {
                "fields": ("views", "reading_time_display", "created_at", "updated_at"),
            },
        ),
        (
            "SEO настройки",
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "Статус и Публикация",
            {
                "fields": ("is_active", "published_at"),
            },
        ),
        (
            "Настройки Hero-секции",
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
    )

    class Media:
        js = ("news/js/category-image.js",)

    actions = ["clear_views_action", "duplicate_news_action", "publish_action", "unpublish_action"]

    def status_display(self, obj):
        """Отображает статус публикации новости с цветовой индикацией."""
        now = timezone.now()
        if not obj.is_active:
            return format_html('<span style="color:#ef4444">● Скрыта</span>')
        if obj.published_at > now:
            return format_html(
                '<span style="color:#f59e0b">● Запланирована</span>'
            )
        return format_html('<span style="color:#10b981">● Активна</span>')
    status_display.short_description = "Статус"

    def reading_time_display(self, obj):
        """Отображает время чтения новости."""
        minutes = obj.get_reading_time
        return format_html(
            '<span style="color:#6366f1">⏱ {} мин.</span>', minutes
        )
    reading_time_display.short_description = "Время чтения"

    def clear_views_button(self, obj):
        """Отображает кнопку для сброса просмотров в списке новостей."""
        return format_html(
            '<a class="button" href="{}" style="padding: 5px 10px; background: #417690; color: white; '
            'text-decoration: none; border-radius: 3px;">Очистить</a>',
            f"{obj.pk}/clear_views/",
        )
    clear_views_button.short_description = "Просмотры"

    def get_urls(self):
        """Добавляет кастомные URL для сброса просмотров."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/clear_views/",
                self.admin_site.admin_view(self.clear_views),
                name="news_clear_views",
            ),
        ]
        return custom_urls + urls

    def clear_views(self, request, object_id, *args, **kwargs):
        """Сбрасывает просмотры для конкретной новости."""
        news = get_object_or_404(News, pk=object_id)
        old_views = news.views
        news.views = 0
        news.save()
        messages.success(
            request,
            f'Количество просмотров для новости "{news.title}" сброшено с {old_views} до 0.',
        )
        return redirect("admin:news_news_changelist")

    @admin.action(description="Сбросить просмотры у выбранных новостей")
    def clear_views_action(self, request, queryset):
        """Массовое действие: сброс просмотров для выбранных новостей."""
        updated_count = queryset.update(views=0)
        self.message_user(
            request, f"Количество просмотров сброшено для {updated_count} новостей."
        )

    @admin.action(description="Дублировать выбранные новости")
    def duplicate_news_action(self, request, queryset):
        """Создаёт копии выбранных новостей (черновики)."""
        count = 0
        for news in queryset:
            # Создаём копию новости
            tags = list(news.tags.all())
            news.pk = None
            news.title = f"[Копия] {news.title}"
            news.slug = ""  # Slug будет сгенерирован автоматически
            news.is_active = False  # Черновик
            news.views = 0
            news.save()
            news.tags.set(tags)
            count += 1
        self.message_user(
            request, f"Создано {count} копий новостей (как черновики)."
        )

    @admin.action(description="Опубликовать выбранные новости")
    def publish_action(self, request, queryset):
        """Публикует выбранные новости."""
        updated = queryset.update(is_active=True, published_at=timezone.now())
        self.message_user(request, f"Опубликовано {updated} новостей.")

    @admin.action(description="Скрыть выбранные новости")
    def unpublish_action(self, request, queryset):
        """Скрывает выбранные новости."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Скрыто {updated} новостей.")
