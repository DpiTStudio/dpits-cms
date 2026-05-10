# mysite/news/utils.py
# Вспомогательные функции для приложения news
# Вынесены из views.py для устранения дублирования кода (принцип DRY)

from django.core.cache import cache
from django.utils import timezone
from .models import News, NewsCategory, NewsTag


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
    if not isinstance(recent_news, list):
        recent_news = list(
            News.objects.filter(is_active=True, published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-published_at")[:5]
        )
        cache.set(cache_key, recent_news, 300)  # 5 минут
    return recent_news


def get_cached_popular_news(limit=5):
    """
    Возвращает список самых популярных новостей (по просмотрам) из кэша.
    Кэшируется на 15 минут.
    """
    cache_key = f"news_popular_{limit}"
    popular = cache.get(cache_key)
    if not isinstance(popular, list):
        popular = list(
            News.objects.filter(is_active=True, published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-views")[:limit]
        )
        cache.set(cache_key, popular, 900)  # 15 минут
    return popular


def get_cached_popular_tags(limit=20):
    """
    Возвращает список самых популярных тегов (по количеству новостей) из кэша.
    Кэшируется на 30 минут.
    """
    from django.db.models import Count
    cache_key = f"news_popular_tags_{limit}"
    tags = cache.get(cache_key)
    if not isinstance(tags, list):
        tags = list(
            NewsTag.objects.annotate(news_count=Count("news"))
            .filter(news_count__gt=0)
            .order_by("-news_count")[:limit]
        )
        cache.set(cache_key, tags, 1800)  # 30 минут
    return tags


def get_cached_news_stats():
    """
    Возвращает общую статистику новостей.
    Кэшируется на 10 минут.
    """
    from django.db.models import Sum, Count
    cache_key = "news_global_stats"
    stats = cache.get(cache_key)
    if not isinstance(stats, dict):
        qs = News.objects.filter(is_active=True, published_at__lte=timezone.now())
        stats = {
            "total_news": qs.count(),
            "total_views": qs.aggregate(total=Sum("views"))["total"] or 0,
            "total_categories": NewsCategory.objects.filter(is_active=True).count(),
            "total_tags": NewsTag.objects.count(),
        }
        cache.set(cache_key, stats, 600)
    return stats


def invalidate_news_cache():
    """
    Сбрасывает все кэши новостей (вызывается при сохранении/удалении новости).
    """
    keys = [
        "news_categories_menu",
        "news_sidebar_recent",
        "news_popular_5",
        "news_popular_10",
        "news_popular_tags_20",
        "news_global_stats",
    ]
    for key in keys:
        cache.delete(key)
