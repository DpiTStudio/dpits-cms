from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import News, NewsCategory


def get_latest_news():
    """Функция для получения последних 3 активных новостей"""
    return (
        News.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")[:3]
    )


def news_list(request):
    """
    Список всех новостей с пагинацией
    """
    news_queryset = (
        News.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )
    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    # Пагинация - 9 новостей на страницу
    paginator = Paginator(news_queryset, 9)
    page = request.GET.get("page")

    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "categories": categories,
            "latest_news": get_latest_news(),
        },
    )


def news_by_category(request, category_slug):
    """
    Новости по категории с пагинацией
    """
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    news_queryset = (
        News.objects.filter(category=category, is_active=True)
        .select_related("category")
        .order_by("-created_at")
    )

    categories = NewsCategory.objects.filter(is_active=True).annotate(
        news_count=Count("news")
    )

    # Пагинация - 9 новостей на страницу
    paginator = Paginator(news_queryset, 9)
    page = request.GET.get("page")

    try:
        news_list = paginator.page(page)
    except PageNotAnInteger:
        news_list = paginator.page(1)
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)

    return render(
        request,
        "news/list.html",
        {
            "news_list": news_list,
            "categories": categories,
            "current_category": category,
            "latest_news": get_latest_news(),
        },
    )


def news_detail(request, slug):
    try:
        news = News.objects.annotate(
            total_comments=Count("comments"), avg_rating=Avg("comments__rating")
        ).get(slug=slug)
    except News.DoesNotExist:
        raise Http404("Новость не найдена")

    # Для отладки - посмотрите что содержит объект
    print(f"Total comments: {news.total_comments}")
    print(f"Avg rating: {news.avg_rating}")
    print(f"Comments exist: {news.comments.exists()}")

    context = {
        "news": news,
        "total_comments": news.total_comments,
        "avg_rating": news.avg_rating if news.avg_rating is not None else 0,
    }
    return render(request, "news/detail.html", context)
