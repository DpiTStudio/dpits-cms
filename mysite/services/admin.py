# services/admin.py
# Назначение: Регистрация моделей в панели администратора Django.
# Позволяет управлять категориями услуг, услугами и заказами через админку.

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ServiceCategory, Service, ServiceOrder, ServiceOrderItem
# ResetAutoIncrementMixin provides a method to reset SQLite auto‑increment counters.
from main.admin_utils import ResetAutoIncrementMixin


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin panel for service categories.
    Provides list view, filters, search and inline editing.
    
    Админ-панель для категорий услуг.
    Определяет, какие поля отображать, фильтровать, искать и редактировать.
    """

    # Поля, отображаемые в списке категорий
    list_display = [
        "name",
        "slug",
        "order",
        "is_active",
        "services_count",
        "views",
        "created_at",
    ]
    # Make the primary identifier clickable
    list_display_links = ("name",)
    # Default ordering by the explicit order field
    ordering = ["order"]
    
    # Поля для фильтрации (сайдбар справа)
    list_filter = [
        "is_active",     # Фильтр по активности
        "created_at",    # Фильтр по дате создания
    ]
    
    # Поля для поиска
    search_fields = ["name", "description"]
    
    # Поля, которые автоматически заполняются из других полей (slug из name)
    prepopulated_fields = {"slug": ("name",)}
    
    # Поля только для чтения (нельзя редактировать)
    readonly_fields = [
        "created_at",
        "updated_at",
        "services_count_display",
    ]
    
    # Поля, которые можно редактировать прямо в списке (без открытия формы)
    list_editable = ["order", "is_active"]
    
    # Количество записей на странице
    list_per_page = 20

    # Группировка полей в форме редактирования
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "image", "description"),
        }),
        ("SEO настройки", {
            "fields": ("seo_title", "seo_keywords", "seo_description"),
        }),
        ("Настройки отображения", {
            "fields": ("show_in_menu", "order", "is_active"),
        }),
        ("Настройки Hero-секции", {
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
            "classes": ("collapse",),  # Сворачиваемая секция
        }),
        ("Системная информация", {
            "fields": ("views", "created_at", "updated_at", "services_count_display"),
            "classes": ("collapse",),
        }),
    )

    def services_count(self, obj: ServiceCategory) -> int:
        """Return the number of services in this category.
        Used in ``list_display``.
        """
        return obj.service_set.count()
    services_count.short_description = "Количество услуг"

    def services_count_display(self, obj: ServiceCategory) -> int:
        """Display the number of services in the edit form (read‑only).
        """
        return obj.service_set.count()
    services_count_display.short_description = "Количество услуг"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin panel for services.
    Handles pricing, images, SEO settings and status flags.
    """

    # Fields displayed in the service list view
    list_display = [
        "id",
        "name",
        "icon_preview",
        "category",
        "price_display",
        "can_order",
        "is_displayed",
        "created_at",
    ]
    # Make the name clickable and order by name by default
    list_display_links = ("name",)
    ordering = ["name"]
    list_select_related = ("category",)

    # Фильтры
    list_filter = [
        "category",          # По категории
        "price_type",        # По типу цены (фикс, от, до, диапазон)
        "currency",          # По валюте
        "can_order",         # Можно ли заказать
        "is_displayed",      # Отображается ли
        "created_at",        # По дате создания
    ]
    
    # Поиск по названию и описаниям
    search_fields = ["name", "short_description", "description"]
    
    # Автозаполнение slug из name
    prepopulated_fields = {"slug": ("name",)}
    
    # Только для чтения (системные поля и превью)
    readonly_fields = [
        "views",
        "created_at",
        "updated_at",
        "icon_preview_large",
        "background_preview_large",
    ]
    # Use raw ID widgets for foreign keys to speed up the admin UI
    raw_id_fields = ("category",)
    # Optimize query count by selecting related category
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category")
    
    # Поля, редактируемые прямо в списке
    list_editable = ["can_order", "is_displayed"]
    
    list_per_page = 20
    date_hierarchy = "created_at"  # Навигация по датам (ссылки год/месяц/день)

    # Группировка полей в форме
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "category", "short_description", "description"),
        }),
        ("Изображения", {
            "fields": ("icon", "icon_preview_large", "background", "background_preview_large"),
        }),
        ("Цены", {
            "fields": ("price_type", "price_fixed", "price_from", "price_to", "currency"),
        }),
        ("Статусы", {
            "fields": ("can_order", "is_displayed"),
        }),
        ("SEO настройки", {
            "fields": ("seo_title", "seo_keywords", "seo_description"),
        }),
        ("Настройки Hero-секции", {
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
        }),
        ("Системная информация", {
            "fields": ("views", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def icon_preview(self, obj: Service) -> str:
        """Render a small thumbnail of the service icon for the list view.
        Returns safe HTML or a placeholder text.
        """
        if obj.icon and getattr(obj.icon, "url", None):
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />',
                obj.icon.url,
            )
        return "Нет иконки"
    icon_preview.short_description = "Иконка"

    def icon_preview_large(self, obj):
        """
        Отображает увеличенную иконку в форме редактирования.
        """
        if obj.icon and obj.icon.url:
            return format_html(
                '<img src="{}" width="200" style="object-fit: cover; border-radius: 8px;" />',
                obj.icon.url,
            )
        return "Нет иконки"
    icon_preview_large.short_description = "Превью иконки"

    def background_preview_large(self, obj: Service) -> str:
        """Render a large preview of the background image in the edit form.
        Returns safe HTML or a placeholder.
        """
        if obj.background and getattr(obj.background, "url", None):
            return format_html(
                '<img src="{}" width="400" style="object-fit: cover; border-radius: 8px;" />',
                obj.background.url,
            )
        return "Нет фона"
    background_preview_large.short_description = "Превью фона"

    def price_display(self, obj):
        """
        Отображает отформатированную цену в списке услуг.
        Использует метод модели get_price_display().
        """
        return obj.get_price_display()
    price_display.short_description = "Цена"


class ServiceOrderItemInline(admin.TabularInline):
    """Inline admin for managing order items directly on a ServiceOrder.
    Uses a tabular layout.
    """
    model = ServiceOrderItem
    extra = 0
    readonly_fields = ("service", "service_name", "price", "quantity", "item_total")
    fields = ("service_name", "service", "price", "quantity", "item_total")
    can_delete = False

    def item_total(self, obj):
        """
        Вычисляет и отображает сумму по позиции (цена × количество).
        """
        return f"{obj.total_price:,.0f} ₽".replace(",", " ")
    item_total.short_description = "Сумма"


@admin.register(ServiceOrder)
class ServiceOrderAdmin(ResetAutoIncrementMixin, admin.ModelAdmin):

    """Admin panel for service orders.
    Provides list, filter, search, and inline order items.
    Inherits ``ResetAutoIncrementMixin`` to reset SQLite auto‑increment counters.
    """

    # Fields displayed in the order list view
    list_display = [
        "id",
        "client_name",
        "client_email",
        "client_phone",
        "order_type_badge",
        "status_badge",
        "total_price_display",
        "items_count",
        "created_at",
    ]
    # Make the ID clickable
    list_display_links = ("id",)
    # Default ordering: newest first
    ordering = ["-created_at"]
    list_select_related = ("user",)
    
    # Фильтры
    list_filter = ["status", "order_type", "created_at"]
    # Use raw ID widget for user foreign key for performance
    raw_id_fields = ("user",)
    
    # Поиск по контактным данным и комментарию
    search_fields = ["client_name", "client_email", "client_phone", "comment"]
    
    # Только для чтения
    readonly_fields = ["created_at", "updated_at", "total_price", "user"]
    
    list_per_page = 25
    date_hierarchy = "created_at"
    inlines = [ServiceOrderItemInline]

    # Additional admin actions
    actions = ["delete_all_orders"]

    # Group fields in the edit form
    fieldsets = (
        ("Клиент", {
            "fields": ("user", "client_name", "client_email", "client_phone"),
        }),
        ("Заказ", {
            "fields": ("order_type", "status", "total_price", "comment"),
        }),
        ("Система", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def delete_all_orders(self, request, queryset):
        """
        Кастомное действие: удаляет все заказы (не только выбранные!) и сбрасывает автоинкремент.
        ВНИМАНИЕ: ИСПРАВЛЕНА ОШИБКА - теперь удаляет только выбранные заказы.
        """
        # Удаляем только выбранные заказы (через queryset, а не все через ServiceOrder.objects.all())
        count = queryset.count()
        queryset.delete()
        
        # Сброс автоинкремента для SQLite
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name = %s",
                [ServiceOrder._meta.db_table]
            )
        self.message_user(request, f"Удалено {count} заказов и автоинкремент сброшен.")
    delete_all_orders.short_description = "Удалить выбранные заказы (и сбросить автоинкремент)"

    def order_type_badge(self, obj):
        """
        Отображает тип заказа в виде цветного бейджа.
        Быстрый (quick) - фиолетовый, Полный (full) - зелёный.
        """
        colors = {"quick": "#6366f1", "full": "#10b981"}
        labels = {"quick": "Быстрый", "full": "Полный"}
        color = colors.get(obj.order_type, "#6b7280")
        label = labels.get(obj.order_type, obj.order_type)
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{}</span>',
            color, label
        )
    order_type_badge.short_description = "Тип"

    def status_badge(self, obj):
        """
        Отображает статус заказа в виде цветного бейджа.
        Новый - синий, В работе - оранжевый, Выполнен - зелёный, Отменён - красный.
        """
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
    status_badge.short_description = "Статус"

    def total_price_display(self, obj) -> str:
        """Display the total order price with thousand‑separator spaces.
        """
        return f"{obj.total_price:,.0f} ₽".replace(",", " ")
    total_price_display.short_description = "Итог"

    def items_count(self, obj) -> int:
        """Return the number of items in the order.
        """
        return obj.items.count()
    items_count.short_description = "Позиций"