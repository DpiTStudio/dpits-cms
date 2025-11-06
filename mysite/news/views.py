# news/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import News, NewsCategory


def news_list(request):
    """Отображение списка всех активных новостей"""
    # Получаем активные новости, отсортированные по дате (новые сверху)
    news_list = News.objects.filter(is_active=True).order_by("-created_at")

    # Получаем активные категории для меню
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Разбиваем на страницы по 20 новостей
    paginator = Paginator(news_list, 20)
    page_number = request.GET.get("page", 1)  # Получаем номер страницы, по умолчанию 1
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы

    # Последние новости для сайдбара
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Формируем данные для шаблона
    context = {
        "news_list": page_obj,
        "categories": categories,
        "recent_news_list": recent_news_list,
        "category": None,  # На главной странице категория не выбрана
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    """Отображение детальной страницы новости"""
    # Получаем новость или показываем ошибку 404
    news = get_object_or_404(News, slug=slug, is_active=True)

    # Увеличиваем счетчик просмотров
    news.increment_views()

    # Получаем активные категории
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Похожие новости (из той же категории)
    similar_news = (
        News.objects.filter(category=news.category, is_active=True)
        .exclude(id=news.id)  # Исключаем текущую новость
        .order_by("-created_at")[:4]  # 4 последние новости
    )

    # Последние новости для сайдбара
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Формируем данные для шаблона
    context = {
        "news": news,
        "similar_news": similar_news,  # Исправлено: было news_list
        "categories": categories,
        "recent_news_list": recent_news_list,
    }
    return render(request, "news/detail.html", context)


def news_by_category(request, slug):
    """Отображение новостей определенной категории"""
    # Получаем категорию или показываем ошибку 404
    category = get_object_or_404(NewsCategory, slug=slug, is_active=True)

    # Новости этой категории
    news_list = News.objects.filter(category=category, is_active=True).order_by(
        "-created_at"
    )

    # Все активные категории для меню
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Разбиваем на страницы
    paginator = Paginator(news_list, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Последние новости для сайдбара
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Формируем данные для шаблона
    context = {
        "category": category,
        "news_list": page_obj,
        "categories": categories,
        "recent_news_list": recent_news_list,
    }
    return render(request, "news/category.html", context)


def news_search(request):
    """Поиск новостей"""
    query = request.GET.get("q", "")
    news_list = News.objects.filter(title__icontains=query, is_active=True)
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]
    context = {
        "news_list": news_list,
        "categories": categories,
        "recent_news_list": recent_news_list,
        "query": query,
    }
    return render(request, "news/search.html", context)


def news_by_tag(request, tag):
    news_list = News.objects.filter(tags__name=tag, is_active=True)
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]
    context = {
        "news_list": news_list,
        "categories": categories,
        "recent_news_list": recent_news_list,
        "tag": tag,
    }
    return render(request, "news/tag.html", context)
