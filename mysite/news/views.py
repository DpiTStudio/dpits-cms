# news/views.py
# Представления (контроллеры) для приложения news (новости)
import datetime
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
)
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone  # Импортируем timezone для работы с датами публикации
from .models import News, NewsCategory, NewsTag
from .utils import get_cached_news_categories, get_cached_sidebar_news
from main.breadcrumbs import get_breadcrumbs


def news_list(request):
    """
    Отображение списка всех активных новостей.
    Оптимизировано с использованием select_related и кэширования.
    """
    query = request.GET.get("q", "")

    sort_by = request.GET.get("sort", "date_desc")

    # Маппинг сортировок (поддержка старых и новых форматов с сайта)
    sort_mapping = {
        "date_desc": "-created_at",
        "views_desc": "-views",
        "category": "category",
        "-created_at": "-created_at",
        "created_at": "created_at",
        "-views": "-views",
        "title": "title",
    }

    db_sort = sort_mapping.get(sort_by, "-created_at")

    category_slug = request.GET.get("category")
    date_filter = request.GET.get("date")

    # Фильтруем активные новости, дата публикации которых уже наступила
    news_queryset = News.objects.filter(
        is_active=True, published_at__lte=timezone.now()
    ).select_related("category")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    if category_slug:
        news_queryset = news_queryset.filter(category__slug=category_slug)

    # Фильтрация по дате публикации (используем published_at, а не created_at)
    if date_filter:
        try:
            parts = date_filter.split("-")
            if len(parts) == 3:
                news_queryset = news_queryset.filter(
                    published_at__year=int(parts[0]),
                    published_at__month=int(parts[1]),
                    published_at__day=int(parts[2]),
                )
            elif len(parts) == 2:
                news_queryset = news_queryset.filter(
                    published_at__year=int(parts[0]), published_at__month=int(parts[1])
                )
            elif len(parts) == 1:
                news_queryset = news_queryset.filter(published_at__year=int(parts[0]))
        except ValueError:
            pass

    # Сортировка
    if db_sort == "category":
        news_queryset = news_queryset.order_by("category__name", "-published_at")
    elif db_sort in ["-created_at", "created_at"]:
        # Для совместимости: маппим сортировку по created_at на published_at
        news_queryset = news_queryset.order_by(
            db_sort.replace("created_at", "published_at")
        )
    else:
        # Для сортировки по просмотрам и т.д. сначала сортируем по выбранному полю, затем по дате
        news_queryset = news_queryset.order_by(db_sort, "-published_at")

    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "selected_category": category_slug or "",
        "current_sort": sort_by,
        "search_query": query,
        "selected_date": date_filter or "",
        "page_title": "Новости",
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
            ]
        ),
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    """
    Отображение детальной страницы новости.
    Оптимизировано с использованием select_related и кэширования.
    """
    news = get_object_or_404(
        News.objects.select_related("category"),
        slug=slug,
        is_active=True,
        published_at__lte=timezone.now(),
    )

    news.increment_views()

    # Умный алгоритм рекомендаций (без изменений)
    news_tags = news.tags.all()
    if news_tags.exists():
        similar_news = (
            News.objects.filter(
                tags__in=news_tags, is_active=True, published_at__lte=timezone.now()
            )
            .exclude(id=news.id)
            .select_related("category")
            .distinct()
            .order_by("-created_at")[:4]
        )

        if len(similar_news) < 4:
            additional_news = (
                News.objects.filter(
                    category=news.category,
                    is_active=True,
                    published_at__lte=timezone.now(),
                )
                .exclude(id=news.id)
                .exclude(id__in=[n.id for n in similar_news])
                .select_related("category")
                .order_by("-created_at")[: 4 - len(similar_news)]
            )
            similar_news = list(similar_news) + list(additional_news)
    else:
        similar_news = (
            News.objects.filter(
                category=news.category, is_active=True, published_at__lte=timezone.now()
            )
            .exclude(id=news.id)
            .select_related("category")
            .order_by("-created_at")[:4]
        )

    # Получаем локальную дату публикации текущей новости (с учётом TIME_ZONE = Europe/Moscow)
    local_pub_date = timezone.localtime(news.published_at).date()

    # ПРАВИЛЬНО: Фильтруем по локальной дате, преобразуя в UTC диапазон
    # Получаем часовой пояс (Europe/Moscow)
    tz = timezone.get_current_timezone()

    # Создаем datetime объекты для начала и конца дня в локальном времени
    local_day_start = datetime.datetime.combine(local_pub_date, datetime.time.min)
    local_day_end = datetime.datetime.combine(local_pub_date, datetime.time.max)

    # Делаем их timezone-aware (локальное время)
    local_day_start_aware = timezone.make_aware(local_day_start, tz)
    local_day_end_aware = timezone.make_aware(local_day_end, tz)

    # Преобразуем в UTC для фильтрации в БД
    utc_day_start = local_day_start_aware.astimezone(timezone.utc)
    utc_day_end = local_day_end_aware.astimezone(timezone.utc)

    # Ограничиваем конец дня текущим моментом (не показываем будущие новости)
    current_utc = timezone.now()
    if utc_day_end > current_utc:
        utc_day_end = current_utc

    # Лента за день: все активные новости, опубликованные именно в этот локальный день
    daily_news = News.objects.filter(
        is_active=True,
        published_at__gte=utc_day_start,
        published_at__lte=utc_day_end,
    ).order_by("published_at")

    # Не показываем ленту, если в ней только текущая новость
    if daily_news.count() <= 1:
        daily_news = []

    context = {
        "news": news,
        "daily_news": daily_news,
        "daily_news_date": local_pub_date,
        "similar_news": similar_news,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (news.category.name, news.category.get_absolute_url()),
                (news.title, reverse("news:detail", kwargs={"slug": news.slug})),
            ]
        ),
    }
    return render(request, "news/detail.html", context)


def news_by_category(request, slug):
    """
    Отображение новостей определённой категории с пагинацией.
    """
    category = get_object_or_404(NewsCategory, slug=slug, is_active=True)

    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "-created_at")
    valid_sorts = {"created_at", "-created_at", "title", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-created_at"

    news_queryset = News.objects.filter(
        category=category, is_active=True, published_at__lte=timezone.now()
    ).select_related("category")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    news_queryset = news_queryset.order_by(sort_by)

    # Защита: убеждаемся, что получили QuerySet, а не случайный объект из кэша
    from django.db.models import QuerySet

    if not isinstance(news_queryset, QuerySet):
        news_queryset = News.objects.none()

    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "selected_category": category.slug,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "current_sort": sort_by,
        "search_query": query,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (category.name, category.get_absolute_url()),
            ]
        ),
    }
    return render(request, "news/category.html", context)


def news_search(request):
    """
    Поиск новостей по запросу пользователя с пагинацией.
    """
    query = request.GET.get("q", "")

    if query:
        news_queryset = (
            News.objects.filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(content__icontains=query),
                is_active=True,
                published_at__lte=timezone.now(),
            )
            .select_related("category")
            .distinct()
            .order_by("-created_at")
        )
    else:
        news_queryset = (
            News.objects.filter(is_active=True, published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-created_at")
        )

    # Пагинация результатов поиска
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "query": query,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (f"Поиск: {query}" if query else "Поиск", request.path),
            ]
        ),
    }
    return render(request, "news/search.html", context)


def news_by_tag(request, slug):
    """
    Отображение новостей с определённым тегом.
    """
    tag = get_object_or_404(NewsTag, slug=slug)

    news_queryset = (
        News.objects.filter(tags=tag, is_active=True, published_at__lte=timezone.now())
        .select_related("category")
        .order_by("-created_at")
    )

    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "tag": tag,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (f"Тег: {tag.name}", request.path),
            ]
        ),
    }
    return render(request, "news/list.html", context)


def get_category_image(request, category_id):
    """
    API endpoint для получения URL изображения категории.
    Используется в админке для автоматической подстановки картинки.
    """
    category = get_object_or_404(NewsCategory, pk=category_id)
    return JsonResponse(
        {
            "image_url": category.image.url if category.image else None,
            "hero_image_url": category.hero_image.url if category.hero_image else None,
        }
    )
