from django import template

register = template.Library()

@register.filter
def get_percent(value, total):
    """
    Вычисляет процентное соотношение value от total.
    Использование: {{ value|get_percent:total }}
    """
    try:
        if not total or float(total) == 0:
            return 0
        return int((float(value) / float(total)) * 100)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
