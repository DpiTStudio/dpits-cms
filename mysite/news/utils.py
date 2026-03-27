# mysite/news/utils.py
# Вспомогательные функции для приложения news
# Вынесены из views.py для устранения дублирования кода (принцип DRY)

from django.core.cache import cache
from .models import News, NewsCategory


def get_cached_news_categories():
    """
    Возвращает список активных категорий новостей из кэша.
    При отсутствии в кэше — делает запрос к БД и кэширует на 10 минут.
    """
    cache_key = "news_categories_menu"
    categories = cache.get(cache_key)
    if not isinstance(categories, list):
        categories = list(
            NewsCategory.objects.filter(is_active=True, show_in_menu=True).order_by(
                "order", "name"
            )
        )
        cache.set(cache_key, categories, 600)  # 10 минут
    return categories


def get_cached_sidebar_news():
    """
    Возвращает список последних 5 новостей для сайдбара из кэша.
    При отсутствии в кэше — делает запрос к БД и кэширует на 5 минут.
    """
    cache_key = "news_sidebar_recent"
    recent_news = cache.get(cache_key)
    if not recent_news:
        recent_news = list(
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:5]
        )
        cache.set(cache_key, recent_news, 300)  # 5 минут
    return recent_news
