# services/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import ServiceCategory, Service, ServiceOrder, ServiceOrderItem


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий услуг"""

    list_display = [
        # Основная информация
        "name",
        "slug",
        # Статусы
        "order",
        "is_active",
        # Статистика
        "services_count",
        "views",
        # Даты
        "created_at",
    ]
    list_filter = [
        # Статусы
        "is_active",
        # Даты
        "created_at",
    ]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        # Даты
        "created_at",
        "updated_at",
        # Статистика
        "services_count_display",
    ]
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
    # Основная информация
    "id", "name", "icon_preview",
    
    # Категория и цена
    "category", "price_display",
    
    # Статусы
    "can_order", "is_displayed",
    
    # Даты
    "created_at",
    ]

    list_filter = [
        # Категория
        "category",
        # Цена
        "price_type",
        "currency",
        # Статусы
        "can_order",
        "is_displayed",
        "created_at",
    ]
    search_fields = ["name", "short_description", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        # Системная информация
        "views",
        "created_at",
        "updated_at",
        # Превью
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

    def price_display(self, obj):
        """Отображение цены в списке"""
        return obj.get_price_display()

    price_display.short_description = _("Цена")


class ServiceOrderItemInline(admin.TabularInline):
    """inline-позиции заказа"""
    model = ServiceOrderItem
    extra = 0
    readonly_fields = ("service", "service_name", "price", "quantity", "item_total")
    fields = ("service_name", "service", "price", "quantity", "item_total")
    can_delete = False

    def item_total(self, obj):
        return f"{obj.total_price:,.0f} ₽".replace(",", " ")
    item_total.short_description = _("Сумма")


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    """Админ-панель заказов"""

    list_display = [
        "id", "client_name", "client_email", "client_phone",
        "order_type_badge", "status_badge", "total_price_display",
        "items_count", "created_at",
    ]
    list_filter = ["status", "order_type", "created_at"]
    search_fields = ["client_name", "client_email", "client_phone", "comment"]
    readonly_fields = ["created_at", "updated_at", "total_price", "user"]
    list_editable = ["status"]
    list_per_page = 25
    date_hierarchy = "created_at"
    inlines = [ServiceOrderItemInline]

    fieldsets = (
        (_("Клиент"), {
            "fields": ("user", "client_name", "client_email", "client_phone"),
        }),
        (_("Заказ"), {
            "fields": ("order_type", "status", "total_price", "comment"),
        }),
        (_("Система"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def order_type_badge(self, obj):
        colors = {"quick": "#6366f1", "full": "#10b981"}
        labels = {"quick": "Быстрый", "full": "Полный"}
        color = colors.get(obj.order_type, "#6b7280")
        label = labels.get(obj.order_type, obj.order_type)
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            color, label
        )
    order_type_badge.short_description = _("Тип")

    def status_badge(self, obj):
        colors = {
            "new": "#3b82f6",
            "in_progress": "#f59e0b",
            "completed": "#10b981",
            "cancelled": "#ef4444",
        }
        labels = dict(ServiceOrder.STATUS_CHOICES)
        color = colors.get(obj.status, "#6b7280")
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            color, label
        )
    status_badge.short_description = _("Статус")

    def total_price_display(self, obj):
        return f"{obj.total_price:,.0f} ₽".replace(",", " ")
    total_price_display.short_description = _("Итог")

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = _("Позиций")

