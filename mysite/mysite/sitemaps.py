# mysite/sitemaps.py
# Конфигурация sitemap.xml для поисковых систем
# Использует встроенный django.contrib.sitemaps

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap для статических страниц"""
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "main:index",
            "main:about",
            "main:contacts",
            "news:list",
            "services:list",
            "reviews:list",
        ]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    """Sitemap для новостей"""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        from news.models import News
        from django.utils import timezone
        return News.objects.filter(is_active=True, published_at__lte=timezone.now()).select_related("category")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class NewsCategorySitemap(Sitemap):
    """Sitemap для категорий новостей"""
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        from news.models import NewsCategory
        return NewsCategory.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()


class ServicesSitemap(Sitemap):
    """Sitemap для услуг"""
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        from services.models import Service
        return Service.objects.filter(is_displayed=True).select_related("category")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class ServicesCategorySitemap(Sitemap):
    """Sitemap для категорий услуг"""
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        from services.models import ServiceCategory
        return ServiceCategory.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()


class PortfolioSitemap(Sitemap):
    """Sitemap для портфолио"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        from portfolio.models import PortfolioItem
        return PortfolioItem.objects.all().select_related("category")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class PagesSitemap(Sitemap):
    """Sitemap для пользовательских страниц"""
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        from main.models import Page
        return Page.objects.filter(show_on_site=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


# Словарь sitemaps для передачи в urls.py
sitemaps = {
    "static": StaticViewSitemap,
    "news": NewsSitemap,
    "news_categories": NewsCategorySitemap,
    "services": ServicesSitemap,
    "services_categories": ServicesCategorySitemap,
    "portfolio": PortfolioSitemap,
    "pages": PagesSitemap,
}
