# news/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import News, NewsCategory


def news_list(request):
    news_list = News.objects.filter(is_active=True).order_by("-created_at")
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Пагинация
    paginator = Paginator(news_list, 9)  # 9 новостей на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "news_list": page_obj,
        "categories": categories,
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_active=True)
    news.increment_views()

    # Похожие новости
    similar_news = (
        News.objects.filter(category=news.category, is_active=True)
        .exclude(id=news.id)
        .order_by("-created_at")[:4]
    )

    context = {
        "news": news,
        "similar_news": similar_news,
    }
    return render(request, "news/detail.html", context)


def news_by_category(request, slug):
    category = get_object_or_404(NewsCategory, slug=slug, is_active=True)
    news_list = News.objects.filter(category=category, is_active=True).order_by(
        "-created_at"
    )
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    paginator = Paginator(news_list, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "news_list": page_obj,
        "categories": categories,
    }
    return render(request, "news/category.html", context)
