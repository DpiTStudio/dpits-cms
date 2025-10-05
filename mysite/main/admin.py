# main/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Админ-панель для настроек сайта.
    Обеспечивает удобное управление всеми настройками через fieldsets.
    """

    list_display = ["slogan", "phone1", "email", "site_closed", "updated_at"]
    list_filter = ["site_closed"]
    readonly_fields = ["updated_at"]

    # Группировка полей для лучшей организации в админке
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("logo", "logo_text", "slogan", "motto", "short_description")},
        ),
        (
            _("Контактная информация"),
            {"fields": ("phone1", "phone2", "email", "address")},
        ),
        (
            _("Социальные сети"),
            {
                "fields": (
                    "facebook",
                    "instagram",
                    "youtube",
                    "rutube",
                    "vk_video",
                    "telegram",
                    "vk",
                    "ok",
                ),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
        (
            _("Статус сайта"),
            {"fields": ("site_closed", "closure_message", "updated_at")},
        ),
        (
            _("Дополнительный контент"),
            {"fields": ("content",), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request):
        """
        Запрещает создание дополнительных записей настроек.
        Разрешает создание только если записей еще нет.
        """
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """
        Запрещает удаление единственной записи настроек.
        """
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Админ-панель для страниц сайта.
    Предоставляет удобное управление страницами с SEO-настройками.
    """

    list_display = [
        "title",
        "slug",
        "show_in_menu",
        "show_on_site",
        "order",
        "updated_at",
    ]
    list_editable = ["show_in_menu", "show_on_site", "order"]
    list_filter = ["show_in_menu", "show_on_site", "created_at"]
    search_fields = ["title", "slug", "content"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("title",)}

    # Организация полей в логические группы
    fieldsets = (
        (_("Основное содержимое"), {"fields": ("title", "slug", "content")}),
        (
            _("Настройки отображения"),
            {"fields": ("show_in_menu", "show_on_site", "order")},
        ),
        (
            _("SEO оптимизация"),
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Мета-информация"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        """
        Добавляет CSS для улучшения внешнего вида админки.
        """

        css = {"all": ("admin/css/pages.css",)}

    def has_add_permission(self, request):
        """
        Запрещает создание дополнительных записей страниц.
        Разрешает создание только если записей еще нет.
        """
        return not Page.objects.exists()
