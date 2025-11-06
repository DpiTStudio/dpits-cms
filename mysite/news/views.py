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
    try:
        page_obj = paginator.get_page(page_number)  # Получение объекта страницы
    except Exception:
        page_obj = paginator.get_page(1)  # Если страница не найдена, возвращаем первую

    # Получение последних новостей для сайдбара
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Формирование контекста для шаблона
    context = {
        "news_list": page_obj,  # Новости текущей страницы
        "categories": categories,  # Список категорий для меню
        "recent_news_list": recent_news_list,  # Последние новости для сайдбара
        "category": None,  # Категория не выбрана на главной странице новостей
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    """Представление для отображения детальной страницы новости."""
    # Получение новости по slug или 404 ошибка если не найдена
    news = get_object_or_404(News, slug=slug, is_active=True)

    # Увеличение счетчика просмотров
    news.increment_views()

    # Получение активных категорий для сайдбара
    categories = NewsCategory.objects.filter(is_active=True, show_in_menu=True)

    # Получение похожих новостей (из той же категории, исключая текущую)
    similar_news = (
        News.objects.filter(category=news.category, is_active=True)
        .exclude(id=news.id)
        .order_by("-created_at")[:4]
    )

    # Получение последних новостей для сайдбара
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Формирование контекста для шаблона
    context = {
        "news": news,
        "similar_news": similar_news,
        "categories": categories,
        "recent_news_list": recent_news_list,
    }
    return render(request, "news/detail.html", context)


def news_by_category(request, slug):
    """
    Представление для отображения новостей, относящихся к определённой категории.

    Функция получает категорию по её slug, извлекает активные новости этой категории,
    разбивает их на страницы с помощью пагинации, а также подготавливает дополнительные
    данные для отображения в шаблоне: список активных категорий для меню и последние
    публикации для сайдбара.

    Параметр `is_active` используется для фильтрации только активных (опубликованных)
    новостей и категорий. Если запрошенная категория не найдена или не активна,
    возвращается ошибка 404.

    Аргументы:
        request (HttpRequest): Объект HTTP-запроса, содержащий данные о запросе,
            включая GET-параметры (например, номер страницы).
        slug (str): Уникальный URL-идентификатор категории (slug), используемый
            для поиска соответствующей категории в базе данных.

    Возвращает:
        HttpResponse: Ответ с отрендеренным HTML-шаблоном 'news/category.html',
        содержащим новости выбранной категории, разбитые на страницы, а также
        дополнительные данные — список категорий для меню и последние новости.

    Используемые компоненты:
        - get_object_or_404: Получает объект категории или возвращает ошибку 404.
        - News.objects.filter: Фильтрует активные новости по категории.
        - Paginator: Разбивает список новостей на страницы (по 20 новостей на страницу).
        - render: Отображает шаблон с переданным контекстом.

    Контекст шаблона:
        category (NewsCategory): Текущая выбранная категория.
        news_list (Page): Объект страницы с новостями текущей категории.
        categories (QuerySet): Список активных категорий, отображаемых в меню.
        recent_news_list (QuerySet): Последние 5 опубликованных новостей для сайдбара.
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
    try:
        page_obj = paginator.get_page(page_number)  # Получение объекта страницы
    except Exception:
        page_obj = paginator.get_page(1)  # Если страница не найдена, возвращаем первую

    # Получение последних новостей для сайдбара
    recent_news_list = News.objects.filter(is_active=True).order_by("-created_at")[:5]

    # Формирование контекста для шаблона
    context = {
        "category": category,  # Текущая категория
        "news_list": page_obj,  # Новости категории текущей страницы
        "categories": categories,  # Список категорий для меню
        "recent_news_list": recent_news_list,  # Последние новости для сайдбара
    }
    return render(request, "news/category.html", context)
