# news/views.py
# Представления (контроллеры) для приложения news (новости)
import datetime
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
)
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import News, NewsCategory, NewsTag
from .utils import (
    get_cached_news_categories,
    get_cached_sidebar_news,
    get_cached_popular_news,
    get_cached_popular_tags,
    get_cached_news_stats,
)
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
        "date_desc": "-published_at",
        "views_desc": "-views",
        "category": "category",
        "-created_at": "-published_at",
        "created_at": "published_at",
        "-views": "-views",
        "title": "title",
    }

    db_sort = sort_mapping.get(sort_by, "-published_at")

    category_slug = request.GET.get("category")
    tag_slug = request.GET.get("tag")
    date_filter = request.GET.get("date")

    # Фильтруем активные новости, дата публикации которых уже наступила
    news_queryset = News.objects.filter(
        is_active=True, published_at__lte=timezone.now()
    ).select_related("category").prefetch_related("tags")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    if category_slug:
        news_queryset = news_queryset.filter(category__slug=category_slug)

    if tag_slug:
        news_queryset = news_queryset.filter(tags__slug=tag_slug)

    # Фильтрация по дате публикации
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
    else:
        news_queryset = news_queryset.order_by(db_sort)

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Активный тег
    active_tag = None
    if tag_slug:
        try:
            active_tag = NewsTag.objects.get(slug=tag_slug)
        except NewsTag.DoesNotExist:
            pass

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_news": get_cached_popular_news(5),
        "popular_tags": get_cached_popular_tags(15),
        "news_stats": get_cached_news_stats(),
        "selected_category": category_slug or "",
        "current_sort": sort_by,
        "search_query": query,
        "selected_date": date_filter or "",
        "active_tag": active_tag,
        "total_count": total_count,
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
        News.objects.select_related("category").prefetch_related("tags"),
        slug=slug,
        is_active=True,
        published_at__lte=timezone.now(),
    )

    news.increment_views()

    # Умный алгоритм рекомендаций
    news_tags = news.tags.all()
    if news_tags.exists():
        similar_news = (
            News.objects.filter(
                tags__in=news_tags, is_active=True, published_at__lte=timezone.now()
            )
            .exclude(id=news.id)
            .select_related("category")
            .distinct()
            .order_by("-published_at")[:4]
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
                .order_by("-published_at")[: 4 - len(similar_news)]
            )
            similar_news = list(similar_news) + list(additional_news)
    else:
        similar_news = (
            News.objects.filter(
                category=news.category, is_active=True, published_at__lte=timezone.now()
            )
            .exclude(id=news.id)
            .select_related("category")
            .order_by("-published_at")[:4]
        )

    # Получаем локальную дату публикации текущей новости
    local_pub_date = timezone.localtime(news.published_at).date()
    tz = timezone.get_current_timezone()

    local_day_start = datetime.datetime.combine(local_pub_date, datetime.time.min)
    local_day_end = datetime.datetime.combine(local_pub_date, datetime.time.max)
    local_day_start_aware = timezone.make_aware(local_day_start, tz)
    local_day_end_aware = timezone.make_aware(local_day_end, tz)
    utc_day_start = local_day_start_aware.astimezone(datetime.timezone.utc)
    utc_day_end = local_day_end_aware.astimezone(datetime.timezone.utc)

    current_utc = timezone.now()
    if utc_day_end > current_utc:
        utc_day_end = current_utc

    # Лента за день
    daily_news = News.objects.filter(
        is_active=True,
        published_at__gte=utc_day_start,
        published_at__lte=utc_day_end,
    ).order_by("published_at")

    if daily_news.count() <= 1:
        daily_news = []

    # Навигация prev/next по категории
    category_news = News.objects.filter(
        category=news.category,
        is_active=True,
        published_at__lte=timezone.now(),
    ).order_by("-published_at")

    ids = list(category_news.values_list("id", flat=True))
    current_idx = ids.index(news.id) if news.id in ids else -1
    prev_news = None
    next_news = None
    if current_idx > 0:
        try:
            prev_news = category_news[current_idx - 1]
        except IndexError:
            pass
    if current_idx >= 0 and current_idx < len(ids) - 1:
        try:
            next_news = category_news[current_idx + 1]
        except IndexError:
            pass

    context = {
        "news": news,
        "daily_news": daily_news,
        "daily_news_date": local_pub_date,
        "similar_news": similar_news,
        "prev_news": prev_news,
        "next_news": next_news,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_news": get_cached_popular_news(5),
        "popular_tags": get_cached_popular_tags(15),
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
    sort_by = request.GET.get("sort", "-published_at")
    valid_sorts = {"published_at", "-published_at", "title", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-published_at"

    news_queryset = News.objects.filter(
        category=category, is_active=True, published_at__lte=timezone.now()
    ).select_related("category").prefetch_related("tags")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    news_queryset = news_queryset.order_by(sort_by)

    from django.db.models import QuerySet
    if not isinstance(news_queryset, QuerySet):
        news_queryset = News.objects.none()

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "selected_category": category.slug,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_news": get_cached_popular_news(5),
        "popular_tags": get_cached_popular_tags(15),
        "current_sort": sort_by,
        "search_query": query,
        "total_count": total_count,
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
            .prefetch_related("tags")
            .distinct()
            .order_by("-published_at")
        )
    else:
        news_queryset = (
            News.objects.filter(is_active=True, published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-published_at")
        )

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_tags": get_cached_popular_tags(15),
        "query": query,
        "total_count": total_count,
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

    sort_by = request.GET.get("sort", "-published_at")
    valid_sorts = {"published_at", "-published_at", "-views", "title"}
    if sort_by not in valid_sorts:
        sort_by = "-published_at"

    news_queryset = (
        News.objects.filter(tags=tag, is_active=True, published_at__lte=timezone.now())
        .select_related("category")
        .prefetch_related("tags")
        .order_by(sort_by)
    )

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Похожие теги (теги, которые часто встречаются вместе с этим)
    related_tags = (
        NewsTag.objects.filter(news__in=news_queryset)
        .exclude(pk=tag.pk)
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:10]
    )

    context = {
        "tag": tag,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_tags": get_cached_popular_tags(15),
        "related_tags": related_tags,
        "current_sort": sort_by,
        "total_count": total_count,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (f"#{tag.name}", request.path),
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


def news_live_search(request):
    """
    AJAX endpoint для живого поиска новостей (autocomplete).
    Возвращает JSON с результатами.
    """
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    results = (
        News.objects.filter(
            Q(title__icontains=query) | Q(short_description__icontains=query),
            is_active=True,
            published_at__lte=timezone.now(),
        )
        .select_related("category")
        .order_by("-published_at")[:8]
    )

    data = [
        {
            "id": n.id,
            "title": n.title,
            "url": n.get_absolute_url(),
            "category": n.category.name if n.category else "",
            "image": n.image.url if n.image else "",
            "date": timezone.localtime(n.published_at).strftime("%d.%m.%Y"),
            "views": n.views,
        }
        for n in results
    ]
    return JsonResponse({"results": data, "query": query})


def news_api_stats(request):
    """
    API endpoint для получения статистики новостей.
    """
    stats = get_cached_news_stats()
    return JsonResponse(stats)
