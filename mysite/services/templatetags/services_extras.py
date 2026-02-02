# services/templatetags/services_extras.py
from django import template
from ..models import ServiceCategory, Service

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить элемент из словаря по ключу"""
    return dictionary.get(key, [])

@register.simple_tag
def get_popular_services_by_category(limit=5):
    """
    Возвращает список категорий с популярными услугами.
    Исключает пустые категории.
    """
    categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')
    result = []
    
    for category in categories:
        # Получаем популярные услуги для категории (сортировка по просмотрам)
        services = Service.objects.filter(
            category=category, 
            is_displayed=True
        ).order_by('-views')[:limit]
        
        if services.exists():
            result.append({
                'category': category,
                'services': services
            })
            
    return result