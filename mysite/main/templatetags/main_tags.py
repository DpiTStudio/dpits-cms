"""
ШАБЛОННЫЕ ТЕГИ И ФИЛЬТРЫ ДЛЯ ПРИЛОЖЕНИЯ MAIN

Этот файл содержит кастомные фильтры и теги для использования в шаблонах Django.
Подключается в шаблоне командой: {% load main_tags %}
"""

from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


# ─────────────────────────────────────────────────
#  Математика и числа
# ─────────────────────────────────────────────────

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


@register.filter
def multiply(value, arg):
    """
    Умножает value на arg.
    Использование: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Делит value на arg.
    Использование: {{ value|divide:100 }}
    """
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def humanize_number(value):
    """
    Форматирует число в человекочитаемый вид с суффиксами.
    Использование: {{ 1500|humanize_number }} → '1.5K'
    Примеры:
        999 → '999'
        1500 → '1.5K'
        1000000 → '1M'
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)

    if num >= 1_000_000:
        result = num / 1_000_000
        return f"{result:.1f}M".rstrip('0').rstrip('.') + 'M' if result != int(result) else f"{int(result)}M"
    elif num >= 1_000:
        result = num / 1_000
        formatted = f"{result:.1f}"
        if formatted.endswith('.0'):
            formatted = formatted[:-2]
        return f"{formatted}K"
    else:
        return str(int(num))


# ─────────────────────────────────────────────────
#  Навигация и URL
# ─────────────────────────────────────────────────

@register.simple_tag(takes_context=True)
def active_url(context, url_name, css_class="active", *args, **kwargs):
    """
    Возвращает css_class если текущий URL совпадает с url_name.
    Использование: {% active_url request 'main:index' %}
    или:           class="nav-link {% active_url request 'main:index' 'active' %}"
    """
    request = context.get("request")
    if not request:
        return ""
    try:
        url = reverse(url_name, args=args, kwargs=kwargs)
        if request.path == url:
            return css_class
    except NoReverseMatch:
        pass
    return ""


@register.simple_tag(takes_context=True)
def active_section(context, path_prefix, css_class="active"):
    """
    Возвращает css_class если текущий URL начинается с path_prefix.
    Использование: class="nav-link {% active_section request '/news/' %}"
    """
    request = context.get("request")
    if not request:
        return ""
    if request.path.startswith(path_prefix):
        return css_class
    return ""


# ─────────────────────────────────────────────────
#  Строки и текст
# ─────────────────────────────────────────────────

@register.filter
def truncate_chars(value, max_length):
    """
    Обрезает строку до max_length символов с '...'.
    Использование: {{ text|truncate_chars:100 }}
    """
    try:
        max_length = int(max_length)
    except (ValueError, TypeError):
        return value
    if not value:
        return value
    value = str(value)
    if len(value) <= max_length:
        return value
    return value[:max_length - 3].rsplit(' ', 1)[0] + '...'


@register.filter
def startswith(value, prefix):
    """
    Возвращает True если строка начинается с prefix.
    Использование: {% if request.path|startswith:'/news/' %}
    """
    try:
        return str(value).startswith(str(prefix))
    except (TypeError, AttributeError):
        return False


@register.filter
def endswith(value, suffix):
    """
    Возвращает True если строка заканчивается на suffix.
    Использование: {% if filename|endswith:'.pdf' %}
    """
    try:
        return str(value).endswith(str(suffix))
    except (TypeError, AttributeError):
        return False


# ─────────────────────────────────────────────────
#  Списки и словари
# ─────────────────────────────────────────────────

@register.filter
def get_item(dictionary, key):
    """
    Получает значение из словаря по ключу.
    Использование: {{ my_dict|get_item:'key' }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def index(lst, i):
    """
    Возвращает элемент списка по индексу.
    Использование: {{ my_list|index:0 }}
    """
    try:
        return lst[int(i)]
    except (IndexError, TypeError, ValueError):
        return None


# ─────────────────────────────────────────────────
#  Утилиты
# ─────────────────────────────────────────────────

@register.filter
def default_if_zero(value, default):
    """
    Возвращает default если value равно 0 или None.
    Использование: {{ views_count|default_if_zero:'нет просмотров' }}
    """
    try:
        if not value or float(value) == 0:
            return default
        return value
    except (TypeError, ValueError):
        return default


@register.simple_tag
def define(val):
    """
    Позволяет объявить переменную в шаблоне.
    Использование: {% define 'some_value' as my_var %}
    """
    return val


@register.inclusion_tag('includes/components/stars_rating.html')
def star_rating(value, max_stars=5):
    """
    Рендерит звёздный рейтинг.
    Использование: {% star_rating review.rating %}
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0
    full = int(value)
    half = 1 if (value - full) >= 0.5 else 0
    empty = int(max_stars) - full - half
    return {
        'full_stars': range(full),
        'half_star': half,
        'empty_stars': range(empty),
        'value': value,
        'max_stars': max_stars,
    }
