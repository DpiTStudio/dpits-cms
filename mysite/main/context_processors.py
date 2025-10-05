# main/context_processors.py
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page


def site_settings(request):
    """
    Контекстный процессор для добавления настроек сайта в каждый шаблон.
    Использует кэширование для оптимизации производительности.
    """
    cache_key = "site_settings"
    settings = cache.get(cache_key)

    if not settings:
        # Получаем настройки из базы, если нет в кэше
        settings = SiteSettings.objects.first()
        if settings:
            # Кэшируем на 5 минут (300 секунд)
            cache.set(cache_key, settings, 300)

    return {"site_settings": settings}


def menu_items(request):
    """
    Контекстный процессор для меню навигации.
    Кэширует список страниц для меню для улучшения производительности.
    """
    cache_key = "menu_pages"
    pages = cache.get(cache_key)

    if not pages:
        # Получаем страницы для меню из базы
        pages = Page.objects.filter(show_in_menu=True, show_on_site=True).order_by(
            "order", "title"
        )

        if pages:
            # Кэшируем на 10 минут (600 секунд)
            cache.set(cache_key, pages, 600)

    return {"menu_pages": pages or []}


def seo_context(request):
    """
    Контекстный процессор для базовых SEO-данных.
    Предоставляет общие SEO-настройки для всех страниц.
    """
    settings = SiteSettings.objects.first()
    return {
        "default_seo_title": getattr(settings, "seo_title", ""),
        "default_seo_description": getattr(settings, "seo_description", ""),
        "default_seo_keywords": getattr(settings, "seo_keywords", ""),
    }
