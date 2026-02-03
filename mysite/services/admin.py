# services/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий услуг"""

    list_display = [
        "name",
        "slug",
        "order",
        "is_active",
        "discount_percentage",
        "discount_active",
        "services_count",
        "views",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at", "services_count_display"]
    list_editable = ["order", "is_active"]
    list_per_page = 20

    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": ("name", "slug", "image", "description"),
            },
        ),
        (
            _("SEO настройки"),
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
            },
        ),
        (
            _("Настройки отображения"),
            {
                "fields": ("show_in_menu", "order", "is_active"),
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
            _("Акции"),
            {
                "fields": ("discount_percentage", "discount_active"),
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": ("views", "created_at", "updated_at", "services_count_display"),
                "classes": ("collapse",),
            },
        ),
    )

    def services_count(self, obj):
        """Количество услуг в категории"""
        return obj.service_set.count()

    services_count.short_description = _("Количество услуг")

    def services_count_display(self, obj):
        """Отображение количества услуг в форме редактирования"""
        return obj.services_count()

    services_count_display.short_description = _("Количество услуг")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Админ-панель для услуг"""

    list_display = [
        "name",
        "category",
        "price_display_full",
        "is_on_sale",
        "can_order",
        "is_displayed",
        "views",
        "created_at",
        "icon_preview",
    ]
    list_filter = [
        "category",
        "price_type",
        "currency",
        "can_order",
        "is_displayed",
        "created_at",
    ]
    search_fields = ["name", "short_description", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "views",
        "created_at",
        "updated_at",
        "icon_preview_large",
        "background_preview_large",
    ]
    list_editable = ["can_order", "is_displayed"]
    list_per_page = 20
    date_hierarchy = "created_at"

    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            _("Изображения"),
            {
                "fields": ("icon", "icon_preview_large", "background", "background_preview_large"),
            },
        ),
        (
            _("Цены"),
            {
                "fields": (
                    "price_type",
                    "price_fixed",
                    "price_from",
                    "price_to",
                    "currency",
                ),
            },
        ),
        (
            _("Акции"),
            {
                "fields": (
                    "discount_percentage",
                    "is_on_sale",
                ),
            },
        ),
        (
            _("Статусы"),
            {
                "fields": ("can_order", "is_displayed"),
            },
        ),
        (
            _("SEO настройки"),
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
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
            _("Системная информация"),
            {
                "fields": ("views", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def icon_preview(self, obj):
        """Превью иконки в списке"""
        if obj.icon:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />',
                obj.icon.url,
            )
        return _("Нет иконки")

    icon_preview.short_description = _("Иконка")

    def icon_preview_large(self, obj):
        """Большое превью иконки в форме редактирования"""
        if obj.icon:
            return format_html(
                '<img src="{}" width="200" style="object-fit: cover; border-radius: 8px;" />',
                obj.icon.url,
            )
        return _("Нет иконки")

    icon_preview_large.short_description = _("Превью иконки")

    def background_preview_large(self, obj):
        """Большое превью фона в форме редактирования"""
        if obj.background:
            return format_html(
                '<img src="{}" width="400" style="object-fit: cover; border-radius: 8px;" />',
                obj.background.url,
            )
        return _("Нет фона")

    background_preview_large.short_description = _("Превью фона")

    def price_display_full(self, obj):
        """Отображение полной цены со скидкой в списке"""
        return format_html(obj.get_full_price_display())

    price_display_full.short_description = _("Цена")
