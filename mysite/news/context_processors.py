# news/context_processors.py
from django.utils import timezone
from .models import News


def latest_news(request):
    latest_news = (
        News.objects.filter(is_active=True, published_at__lte=timezone.now())
        .order_by("-created_at")[:3]
    )
    return {"latest_news": latest_news}
