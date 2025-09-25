# main/admin.py

from django.contrib import admin
from .models import SiteSettings, Page


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["slogan", "phone1", "phone2", "email", "site_closed"]
    fieldsets = (
        ("Контакты", {"fields": ("phone1", "phone2", "email")}),
        ("Логотип и текст", {"fields": ("logo", "logo_text", "slogan")}),
        ("Информация о сайте", {"fields": ("motto", "short_description")}),
        (
            "Социальные сети",
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
                )
            },
        ),
        ("Описание", {"fields": ("content", "address")}),
        ("Статус сайта", {"fields": ("site_closed", "closure_message")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "show_in_menu", "show_on_site", "order"]
    list_editable = ["show_in_menu", "show_on_site", "order"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Основная информация", {"fields": ("title", "slug", "content")}),
        (
            "Настройки отображения",
            {"fields": ("show_in_menu", "show_on_site", "order")},
        ),
        ("SEO настройки", {"fields": ("seo_title", "seo_keywords", "seo_description")}),
    )
