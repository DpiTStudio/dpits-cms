# news/context_processors.py
from .models import News


def latest_news(request):
    latest_news = News.objects.filter(is_active=True).order_by("-created_at")[:3]
    return {"latest_news": latest_news}
