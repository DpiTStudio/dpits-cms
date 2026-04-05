from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import path
from django.utils.html import format_html
from .models import NewsCategory, News, NewsTag


@admin.register(NewsTag)
class NewsTagAdmin(admin.ModelAdmin):
    """Управление тегами новостей."""
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления категориями новостей.
    Поддержка SEO, сортировки, отображения в меню и управления активностью.
    """

    list_display = ["name", "slug", "show_in_menu", "order", "is_active"]
    list_editable = ["show_in_menu", "order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}

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


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления новостями.
    Поддержка фильтрации, SEO, сброса просмотров (массово и для отдельных записей).
    """

    list_display = [
        "title",
        "category",
        "views",
        "is_active",
        "created_at",
        "clear_views_button",
    ]
    list_filter = ["category", "is_active", "created_at", "tags"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["views", "created_at", "updated_at"]
    filter_horizontal = ["tags"]  # Удобный виджет для выбора тегов

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
                "fields": ("views", "created_at", "updated_at"),
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
            "Статус",
            {
                "fields": ("is_active",),
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

    actions = ["clear_views_action"]

    def clear_views_button(self, obj):
        """Отображает кнопку для сброса просмотров в списке новостей."""
        return format_html(
            '<a class="button" href="{}" style="padding: 5px 10px; background: #417690; color: white; '
            'text-decoration: none; border-radius: 3px;">Очистить</a>',
            f"{obj.pk}/clear_views/",
        )

    clear_views_button.short_description = "Очистить просмотры"
    # Удалено allow_tags — больше не требуется, так как format_html безопасен по умолчанию

    def get_urls(self):
        """Добавляет кастомный URL для сброса просмотров."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/clear_views/",
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
