from django.contrib import admin
from main.admin_utils import ResetAutoIncrementMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import path
from django.utils.html import format_html
from django.utils import timezone
from .models import NewsCategory, News, NewsTag, Comment, NewsReaction


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

    list_display = [
        "name",
        "slug",
        "news_count_display",
        "show_in_menu",
        "order",
        "is_active",
        "views",
    ]
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
                    "hero_is_active",
                    "hero_title",
                    "hero_subtitle",
                    "hero_image",
                    "hero_bg_type",
                    "hero_bg_color",
                    "hero_bg_gradient",
                    "hero_show_particles",
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
        # Вся информация о новости в одной строке
        "news_info_display",
        # Действия
        "clear_views_button",
    ]

    list_per_page = 20
    list_filter = ["category", "is_active", "published_at", "created_at", "tags"]
    list_editable = []
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
                    "hero_is_active",
                    "hero_title",
                    "hero_subtitle",
                    "hero_image",
                    "hero_bg_type",
                    "hero_bg_color",
                    "hero_bg_gradient",
                    "hero_show_particles",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    class Media:
        js = ("news/js/category-image.js",)

    actions = [
        "clear_views_action",
        "duplicate_news_action",
        "publish_action",
        "unpublish_action",
    ]

    def news_info_display(self, obj):
        """
        Одна строка в списке новостей:
          Строка 1 — Название (жирный)
          Строка 2 — 📁 Категория  ● Статус  ⏱️ Время  📅 Создана  🕒 Опубликована  👁️ Просмотры
        """
        now = timezone.now()
        category_name = obj.category.name if obj.category else "—"

        # Статус
        if not obj.is_active:
            status_html = '<span style="color:#ef4444">● Скрыта</span>'
        elif obj.published_at > now:
            status_html = '<span style="color:#f59e0b">● Запланирована</span>'
        else:
            status_html = '<span style="color:#10b981">● Активна</span>'

        minutes = obj.get_reading_time
        created = obj.created_at.strftime("%d.%m.%Y") if obj.created_at else "—"
        published = obj.published_at.strftime("%d.%m.%Y %H:%M") if obj.published_at else "—"

        return format_html(
            '<span style="font-weight:600;font-size:13px">{title}</span>'
            '<br>'
            '<span style="color:#888;font-size:11px">'
            '📁 {cat}&nbsp;&nbsp;{status}&nbsp;&nbsp;'
            '⏱️ {min}&nbsp;мин.&nbsp;&nbsp;'
            '📅 {created}&nbsp;&nbsp;'
            '🕒 {published}&nbsp;&nbsp;'
            '👁️ {views}'
            '</span>',
            title=obj.title,
            cat=category_name,
            status=format_html(status_html),
            min=minutes,
            created=created,
            published=published,
            views=obj.views,
        )

    news_info_display.short_description = "Новость"
    news_info_display.admin_order_field = "title"

    def reading_time_display(self, obj):
        """Время чтения (используется в fieldsets)."""
        minutes = obj.get_reading_time
        return format_html('<span style="color:#6366f1">⏱ {} мин.</span>', minutes)

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
            tags = list(news.tags.all())
            news.pk = None
            news.title = f"[Копия] {news.title}"
            news.slug = ""  # Slug будет сгенерирован автоматически
            news.is_active = False  # Черновик
            news.views = 0
            news.save()
            news.tags.set(tags)
            count += 1
        self.message_user(request, f"Создано {count} копий новостей (как черновики).")

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


@admin.register(Comment)
class CommentAdmin(ResetAutoIncrementMixin, admin.ModelAdmin):
    """Админ-панель для управления комментариями к новостям."""

    list_display = ["news_link", "author_display", "content_truncated", "is_approved", "created_at", "parent_display"]
    list_filter = ["is_approved", "created_at"]
    list_editable = ["is_approved"]
    search_fields = ["content", "name", "email", "user__username", "news__title"]
    actions = ["approve_comments", "disapprove_comments"]
    readonly_fields = ["created_at", "updated_at"]

    def news_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            obj.news.get_absolute_url(),
            obj.news.title[:30] + "..." if len(obj.news.title) > 30 else obj.news.title
        )
    news_link.short_description = "Новость"

    def author_display(self, obj):
        if obj.user:
            return format_html('<span style="font-weight:bold;color:#4f46e5">{}</span>', obj.user.username)
        return format_html('<span>{} (Гость)</span>', obj.name)
    author_display.short_description = "Автор"

    def content_truncated(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_truncated.short_description = "Текст комментария"

    def parent_display(self, obj):
        if obj.parent:
            return f"Ответ на #{obj.parent.id}"
        return "—"
    parent_display.short_description = "Родитель"

    @admin.action(description="Одобрить выбранные комментарии")
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Одобрено {updated} комментариев.")

    @admin.action(description="Скрыть выбранные комментарии")
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"Скрыто {updated} комментариев.")


@admin.register(NewsReaction)
class NewsReactionAdmin(ResetAutoIncrementMixin, admin.ModelAdmin):
    """Админ-панель для управления реакциями на новости."""

    list_display = ["news_title", "reaction_type", "session_key", "ip_address", "created_at"]
    list_filter = ["reaction_type", "created_at"]
    search_fields = ["news__title", "ip_address", "session_key"]
    readonly_fields = ["news", "reaction_type", "session_key", "ip_address", "created_at"]

    def news_title(self, obj):
        return obj.news.title
    news_title.short_description = "Новость"

