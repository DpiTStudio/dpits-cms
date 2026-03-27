# news/feeds.py
# RSS-лента для новостей сайта
# Использует встроенный django.contrib.syndication

from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from .models import News, NewsCategory


class LatestNewsFeed(Feed):
    """RSS-лента последних новостей сайта"""

    feed_type = Rss201rev2Feed
    title = "Последние новости"
    description = "Актуальные новости и обновления"
    language = "ru"

    def link(self):
        return reverse("news:list")

    def items(self):
        return (
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.short_description or item.title

    def item_pubdate(self, item):
        return item.created_at

    def item_categories(self, item):
        return [item.category.name] if item.category else []

    def item_author_name(self, item):
        return ""

    def item_link(self, item):
        return item.get_absolute_url()


class NewsByCategoryFeed(Feed):
    """RSS-лента новостей конкретной категории"""

    feed_type = Rss201rev2Feed
    language = "ru"

    def get_object(self, request, slug):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(NewsCategory, slug=slug, is_active=True)

    def title(self, obj):
        return f"Новости: {obj.name}"

    def description(self, obj):
        return f"Последние новости из категории «{obj.name}»"

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return (
            News.objects.filter(category=obj, is_active=True)
            .select_related("category")
            .order_by("-created_at")[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.short_description or item.title

    def item_pubdate(self, item):
        return item.created_at

    def item_link(self, item):
        return item.get_absolute_url()
