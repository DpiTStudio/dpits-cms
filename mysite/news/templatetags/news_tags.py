# news/templatetags/news_tags.py
# Кастомные теги и фильтры для шаблонов приложения news

from django import template
from django.utils import timezone

register = template.Library()

# Месяцы в родительном падеже (Genitive case) — для формата "06 мая 2026"
MONTHS_GENITIVE = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


@register.filter(name="ru_date")
def ru_date(value, fmt="full"):
    """
    Форматирует дату/datetime в русский формат с правильным падежом.

    Форматы:
      "full"  → "06 мая 2026"         (день + месяц в род. падеже + год)
      "short" → "06 мая"              (день + месяц без года)
      "time"  → "21:09"               (только время)
      "dt"    → "06 мая 2026, 21:09"  (полная дата и время)

    Использование в шаблоне:
      {% load news_tags %}
      {{ news.published_at|ru_date }}
      {{ news.published_at|ru_date:"dt" }}
    """
    if not value:
        return ""

    try:
        # Если передан datetime — конвертируем в локальное время
        if hasattr(value, "tzinfo") and value.tzinfo is not None:
            value = timezone.localtime(value)

        day = value.day
        month = MONTHS_GENITIVE.get(value.month, "")
        year = value.year
        hour = value.strftime("%H")
        minute = value.strftime("%M")

        if fmt == "short":
            return f"{day:02d} {month}"
        elif fmt == "time":
            return f"{hour}:{minute}"
        elif fmt == "dt":
            return f"{day:02d} {month} {year}, {hour}:{minute}"
        else:  # full (default)
            return f"{day:02d} {month} {year}"
    except (AttributeError, TypeError):
        return str(value)
