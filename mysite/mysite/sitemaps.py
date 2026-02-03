from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from news.models import News
from portfolio.models import PortfolioItem
from services.models import Service
from main.models import Page

class StaticViewSitemap(Sitemap):
    """Карта сайта для статических страниц (главная, контакты и т.д.)"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'main:index',
            'news:list',
            'portfolio:list',
            'services:list',
            'reviews:list',
            'feedback:contact',
        ]

    def location(self, item):
        return reverse(item)

class PageSitemap(Sitemap):
    """Карта сайта для динамических страниц из CMS"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Page.objects.filter(show_on_site=True)

    def lastmod(self, obj):
        return obj.updated_at

class NewsSitemap(Sitemap):
    """Карта сайта для новостей"""
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return News.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class PortfolioSitemap(Sitemap):
    """Карта сайта для портфолио"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return PortfolioItem.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class ServiceSitemap(Sitemap):
    """Карта сайта для услуг"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_displayed=True)

    def lastmod(self, obj):
        return obj.updated_at
