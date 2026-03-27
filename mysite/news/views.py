# news/views.py
# Представления (контроллеры) для приложения news (новости)
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
)
from django.core.paginator import Paginator
from django.db.models import Q
from .models import News, NewsCategory, NewsTag
from .utils import get_cached_news_categories, get_cached_sidebar_news
from main.breadcrumbs import get_breadcrumbs


def news_list(request):
    """
    Отображение списка всех активных новостей.
    Оптимизировано с использованием select_related и кэширования.
    """
    query = request.GET.get("q", "")

    sort_by = request.GET.get("sort", "-created_at")
    valid_sorts = {"created_at", "-created_at", "title", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-created_at"

    category_slug = request.GET.get("category")

    news_queryset = News.objects.filter(is_active=True).select_related("category")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    if category_slug:
        news_queryset = news_queryset.filter(category__slug=category_slug)

    news_queryset = news_queryset.order_by(sort_by)

    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "recent_news_list": get_cached_sidebar_news(),
        "selected_category": category_slug or "",
        "current_sort": sort_by,
        "search_query": query,
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
        ]),
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    """
    Отображение детальной страницы новости.
    Оптимизировано с использованием select_related и кэширования.
    """
    news = get_object_or_404(
        News.objects.select_related("category"), slug=slug, is_active=True
    )

    news.increment_views()

    similar_news = (
        News.objects.filter(category=news.category, is_active=True)
        .select_related("category")
        .exclude(id=news.id)
        .order_by("-created_at")[:4]
    )

    context = {
        "news": news,
        "similar_news": similar_news,
        "categories": get_cached_news_categories(),
        "recent_news_list": get_cached_sidebar_news(),
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (news.category.name, news.category.get_absolute_url()),
            (news.title, reverse("news:detail", kwargs={"slug": news.slug})),
        ]),
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

    news_queryset = (
        News.objects.filter(category=category, is_active=True)
        .select_related("category")
    )

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    news_queryset = news_queryset.order_by(sort_by)

    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "selected_category": category.slug,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "recent_news_list": get_cached_sidebar_news(),
        "current_sort": sort_by,
        "search_query": query,
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (category.name, category.get_absolute_url()),
        ]),
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
            )
            .select_related("category")
            .distinct()
            .order_by("-created_at")
        )
    else:
        news_queryset = (
            News.objects.filter(is_active=True)
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
        "recent_news_list": get_cached_sidebar_news(),
        "query": query,
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (f"Поиск: {query}" if query else "Поиск", request.path),
        ]),
    }
    return render(request, "news/search.html", context)


def news_by_tag(request, slug):
    """
    Отображение новостей с определённым тегом.
    """
    tag = get_object_or_404(NewsTag, slug=slug)

    news_queryset = (
        News.objects.filter(tags=tag, is_active=True)
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
        "recent_news_list": get_cached_sidebar_news(),
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (f"Тег: {tag.name}", request.path),
        ]),
    }
    return render(request, "news/list.html", context)
