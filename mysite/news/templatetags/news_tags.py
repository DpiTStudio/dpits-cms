# news/templatetags/news_tags.py
# Кастомные теги и фильтры для шаблонов приложения news

from django import template
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Месяцы в родительном падеже (Genitive case) — для формата «06 мая 2026»
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

# Nominative (for headings like "май 2026")
MONTHS_NOMINATIVE = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
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
      "month" → "Май 2026"            (именительный + год)

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
        month_gen = MONTHS_GENITIVE.get(value.month, "")
        month_nom = MONTHS_NOMINATIVE.get(value.month, "")
        year = value.year
        hour = value.strftime("%H")
        minute = value.strftime("%M")

        if fmt == "short":
            return f"{day:02d} {month_gen}"
        elif fmt == "time":
            return f"{hour}:{minute}"
        elif fmt == "dt":
            return f"{day:02d} {month_gen} {year}, {hour}:{minute}"
        elif fmt == "month":
            return f"{month_nom} {year}"
        elif fmt == "relative":
            now = timezone.now()
            if hasattr(value, "tzinfo") and value.tzinfo is None:
                import datetime
                value = timezone.make_aware(datetime.datetime.combine(value, datetime.time()))
            diff = now - value if hasattr(value, "hour") else None
            if diff:
                total_seconds = int(diff.total_seconds())
                if total_seconds < 60:
                    return "только что"
                elif total_seconds < 3600:
                    mins = total_seconds // 60
                    return f"{mins} мин. назад"
                elif total_seconds < 86400:
                    hrs = total_seconds // 3600
                    return f"{hrs} ч. назад"
                elif total_seconds < 604800:
                    days = total_seconds // 86400
                    return f"{days} дн. назад"
            return f"{day:02d} {month_gen} {year}"
        else:  # full (default)
            return f"{day:02d} {month_gen} {year}"
    except (AttributeError, TypeError):
        return str(value)


@register.filter(name="reading_time")
def reading_time(value):
    """
    Возвращает приблизительное время чтения текста в минутах.
    Принимает HTML-строку или число слов.
    """
    if not value:
        return 1
    try:
        from django.utils.html import strip_tags
        import math
        plain = strip_tags(str(value))
        words = len(plain.split())
        minutes = math.ceil(words / 200)
        return max(1, minutes)
    except Exception:
        return 1


@register.filter(name="plural_ru")
def plural_ru(value, variants):
    """
    Русское склонение существительных по числу.
    variants — строка вида "просмотр,просмотра,просмотров"

    Пример: {{ news.views|plural_ru:"просмотр,просмотра,просмотров" }}
    """
    try:
        n = abs(int(value))
        parts = str(variants).split(",")
        if len(parts) != 3:
            return parts[0] if parts else ""
        if 11 <= n % 100 <= 19:
            return parts[2]
        rem = n % 10
        if rem == 1:
            return parts[0]
        elif 2 <= rem <= 4:
            return parts[1]
        else:
            return parts[2]
    except (ValueError, TypeError):
        return ""


@register.filter(name="truncate_chars")
def truncate_chars(value, max_length):
    """Обрезает строку до max_length символов с многоточием."""
    try:
        from django.utils.html import strip_tags
        text = strip_tags(str(value))
        max_length = int(max_length)
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(" ", 1)[0] + "…"
    except Exception:
        return value


@register.filter(name="is_hot")
def is_hot(news_obj, threshold=100):
    """
    Возвращает True, если новость «горячая» (много просмотров).
    Порог по умолчанию — 100 просмотров.
    """
    try:
        return int(getattr(news_obj, "views", 0)) >= int(threshold)
    except (ValueError, TypeError):
        return False


@register.filter(name="is_new")
def is_new(news_obj, hours=24):
    """
    Возвращает True, если новость опубликована менее чем hours часов назад.
    """
    try:
        import datetime
        pub = getattr(news_obj, "published_at", None)
        if not pub:
            return False
        if pub.tzinfo is None:
            pub = timezone.make_aware(pub)
        delta = timezone.now() - pub
        return delta.total_seconds() < int(hours) * 3600
    except Exception:
        return False


@register.simple_tag
def news_stats_badge(news_obj):
    """
    Возвращает HTML-бейдж «Горячее» или «Новое» для карточки новости.
    """
    badges = []
    try:
        pub = getattr(news_obj, "published_at", None)
        views = getattr(news_obj, "views", 0)
        if pub:
            if pub.tzinfo is None:
                pub = timezone.make_aware(pub)
            delta = timezone.now() - pub
            if delta.total_seconds() < 86400:  # < 24h
                badges.append('<span class="news-badge-new"><i class="fas fa-bolt"></i> Новое</span>')
        if int(views) >= 100:
            badges.append('<span class="news-badge-hot"><i class="fas fa-fire"></i> Горячее</span>')
    except Exception:
        pass
    return mark_safe("".join(badges))


@register.inclusion_tag("news/components/tag_cloud.html")
def tag_cloud(limit=15):
    """
    Рендерит облако тегов с наиболее часто используемыми тегами.
    """
    from news.models import NewsTag
    from django.db.models import Count
    tags = (
        NewsTag.objects
        .annotate(news_count=Count("news"))
        .filter(news_count__gt=0)
        .order_by("-news_count")[:limit]
    )
    return {"tags": tags}


@register.inclusion_tag("news/components/popular_news.html")
def popular_news_widget(limit=5):
    """
    Рендерит виджет популярных новостей (по просмотрам).
    """
    from news.utils import get_cached_popular_news
    return {"popular_news": get_cached_popular_news(limit)}
