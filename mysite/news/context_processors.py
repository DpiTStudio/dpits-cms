# news/context_processors.py
from django.utils import timezone
from django.core.cache import cache
from .models import News


def latest_news(request):
    """
    Контекстный процессор для отображения последних новостей в глобальных шаблонах.
    Кэшируется на 5 минут для производительности.
    """
    cache_key = "ctx_latest_news_3"
    cached = cache.get(cache_key)
    if cached is None:
        cached = list(
            News.objects.filter(is_active=True, published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-published_at")[:3]
        )
        cache.set(cache_key, cached, 300)
    return {"latest_news": cached}
