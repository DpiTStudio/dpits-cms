from django import template
from django.db.models import Sum

register = template.Library()


@register.filter
def sum_news_count(categories):
    """Суммирует количество новостей во всех категориях"""
    return categories.aggregate(total=Sum("news_count"))["total"] or 0
