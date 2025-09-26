# news/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import News, NewsCategory


def news_list(request):
    """Представление для отображения списка всех активных новостей
    и категорий в меню.

    Args:
        request: HTTP-запрос

    Returns:
        HttpResponse: Отрендеренный шаблон со списком новостей
    """
    # Получение всех активных новостей, отсортированных по дате (новые сначала)
    news_list = News.objects.filter(is_active=True).order_by("-created_at")

    # Получение активных категорий для отображения в меню
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Пагинация - 20 новостей на страницу
    paginator = Paginator(news_list, 20)
    page_number = request.GET.get("page")  # Получение номера страницы из GET-параметра
    page_obj = paginator.get_page(page_number)  # Получение объекта страницы

    # Формирование контекста для шаблона
    context = {
        "news_list": page_obj,  # Новости текущей страницы
        "categories": categories,  # Список категорий для меню
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    """Представление для отображения детальной страницы новости.

    Args:
        request: HTTP-запрос
        slug (str): URL-идентификатор новости

    Returns:
        HttpResponse: Отрендеренный шаблон с детальной информацией о новости
    """
    # Получение новости по slug или 404 ошибка если не найдена
    news = get_object_or_404(News, slug=slug, is_active=True)

    # Увеличение счетчика просмотров
    news.increment_views()

    # Получение активных категорий для сайдбара
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Получение похожих новостей (из той же категории, исключая текущую)
    similar_news = (
        News.objects.filter(category=news.category, is_active=True)
        .exclude(id=news.id)  # Исключение текущей новости
        .order_by("-created_at")[:4]  # 4 последние новости из категории
    )

    # Формирование контекста для шаблона
    context = {
        "news": news,  # Текущая новость
        "similar_news": similar_news,  # Похожие новости для сайдбара
        "categories": categories,  # Категории для сайдбара
    }
    return render(request, "news/detail.html", context)


def news_by_category(request, slug):
    """
    Представление для отображения новостей определенной категории.

    Args:
        request: HTTP-запрос
        slug (str): URL-идентификатор категории

    Returns:
        HttpResponse: Отрендеренный шаблон с новостями категории
    """
    # Получение категории по slug или 404 ошибка если не найдена
    category = get_object_or_404(NewsCategory, slug=slug, is_active=True)

    # Получение активных новостей данной категории
    news_list = News.objects.filter(category=category, is_active=True).order_by(
        "-created_at"
    )

    # Получение активных категорий для меню
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Пагинация - 20 новостей на страницу
    paginator = Paginator(news_list, 20)
    page_number = request.GET.get("page")  # Получение номера страницы из GET-параметра
    page_obj = paginator.get_page(page_number)  # Получение объекта страницы

    # Формирование контекста для шаблона
    context = {
        "category": category,  # Текущая категория
        "news_list": page_obj,  # Новости категории текущей страницы
        "categories": categories,  # Список категорий для меню
    }
    return render(request, "news/category.html", context)
