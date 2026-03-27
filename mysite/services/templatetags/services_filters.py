# mysite/services/templatetags/services_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить элемент из словаря по ключу"""
    return dictionary.get(key, [])

@register.filter
def split(value, delimiter=','):
    """Разделить строку по разделителю"""
    return value.split(delimiter)