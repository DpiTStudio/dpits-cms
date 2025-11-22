# context_processors.py
# Контекстные процессоры для добавления данных в шаблоны
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
        settings = SiteSettings.load()
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
            cache.set(cache_key, list(pages), 600)
        else:
            pages = []

    return {"menu_pages": pages}


def sidebar_data(request):
    """
    Контекстный процессор для данных сайдбара.
    Возвращает последние новости, работы портфолио и отзывы.
    Использует кэширование для оптимизации производительности.
    """
    cache_key = "sidebar_data"
    sidebar_data = cache.get(cache_key)

    if not sidebar_data:
        sidebar_data = {}

        # Получаем 3 последние новости
        try:
            from news.models import News
            sidebar_data["sidebar_news"] = list(
                News.objects.filter(is_active=True).order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_news"] = []

        # Получаем 3 последние работы из портфолио
        try:
            from portfolio.models import PortfolioItem
            sidebar_data["sidebar_portfolio"] = list(
                PortfolioItem.objects.filter(status="published")
                .order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_portfolio"] = []

        # Получаем 3 последних отзыва
        try:
            from reviews.models import Review
            sidebar_data["sidebar_reviews"] = list(
                Review.objects.filter(status="approved").order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_reviews"] = []

        # Кэшируем на 10 минут (600 секунд)
        cache.set(cache_key, sidebar_data, 600)

    return sidebar_data


def seo_context(request):
    """
    Контекстный процессор для базовых SEO-данных.
    Предоставляет общие SEO-настройки для всех страниц.
    """
    settings = SiteSettings.load()
    return {
        "default_seo_title": getattr(settings, "seo_title", ""),
        "default_seo_description": getattr(settings, "seo_description", ""),
        "default_seo_keywords": getattr(settings, "seo_keywords", ""),
    }
