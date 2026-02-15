# news/views.py
# Представления (контроллеры) для приложения news (новости)
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
)  # Импорт функций для рендеринга шаблонов и получения объектов
from django.core.paginator import (
    Paginator,
)  # Импорт класса для пагинации (разбиения на страницы)
from django.core.cache import cache  # Импорт кэша для оптимизации производительности
from django.db.models import Q  # Импорт Q-объекта для сложных запросов
from .models import News, NewsCategory  # Импорт моделей новостей и категорий
from main.breadcrumbs import get_breadcrumbs


def news_list(request):
    """
    Отображение списка всех активных новостей.
    Оптимизировано с использованием select_related для уменьшения количества запросов к БД.

    Args:
        request: HTTP-запрос от пользователя

    Returns:
        HttpResponse: Отрендеренный шаблон со списком новостей
    """
    # Получаем параметр поиска
    query = request.GET.get("q", "")
    
    # Сортировка
    sort_by = request.GET.get("sort", "-created_at")
    valid_sorts = {"created_at", "-created_at", "title", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-created_at"
    
    # Фильтрация по категории из GET (для универсальности)
    category_slug = request.GET.get("category")
    
    # Базовый запрос
    news_queryset = News.objects.filter(is_active=True).select_related("category")
    
    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(content__icontains=query)
        )
        
    if category_slug:
        news_queryset = news_queryset.filter(category__slug=category_slug)
    
    news_queryset = news_queryset.order_by(sort_by)

    # Получаем активные категории для меню
    cache_key = "news_categories_menu"
    categories = cache.get(cache_key)
    if not categories:
        categories = list(
            NewsCategory.objects.filter(is_active=True, show_in_menu=True).order_by(
                "order", "name"
            )
        )
        cache.set(cache_key, categories, 600)  # Кэш на 10 минут

    # Разбиваем на страницы
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Последние новости для сайдбара
    # ИСПРАВЛЕНО: Используем кэш для последних новостей
    cache_key_sidebar = "news_sidebar_recent"
    recent_news_list = cache.get(cache_key_sidebar)
    if not recent_news_list:
        recent_news_list = list(
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:5]
        )
        cache.set(cache_key_sidebar, recent_news_list, 300)  # Кэш на 5 минут

    # Формируем данные для шаблона
    context = {
        "news_list": page_obj,
        "categories": categories,
        "recent_news_list": recent_news_list,
        "selected_category": category_slug or "",
        "current_sort": sort_by,
        "search_query": query,
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
        ]),
    }
    return render(
        request, "news/list.html", context
    )  # Рендерим шаблон со списком новостей


def news_detail(request, slug):
    """
    Отображение детальной страницы новости.
    Оптимизировано с использованием select_related для уменьшения количества запросов к БД.

    Args:
        request: HTTP-запрос от пользователя
        slug: URL-дружественный идентификатор новости

    Returns:
        HttpResponse: Отрендеренный шаблон с детальной информацией о новости
    """
    # Получаем новость или показываем ошибку 404
    # ИСПРАВЛЕНО: Добавлен select_related для оптимизации запроса к категории
    news = get_object_or_404(
        News.objects.select_related("category"), slug=slug, is_active=True
    )

    # Увеличиваем счетчик просмотров
    news.increment_views()  # Увеличиваем счетчик просмотров на 1

    # Получаем активные категории
    # ИСПРАВЛЕНО: Используем кэш для категорий
    cache_key = "news_categories_menu"
    categories = cache.get(cache_key)
    if not categories:
        categories = list(
            NewsCategory.objects.filter(is_active=True, show_in_menu=True).order_by(
                "order", "name"
            )
        )
        cache.set(cache_key, categories, 600)  # Кэш на 10 минут

    # Похожие новости (из той же категории)
    # ИСПРАВЛЕНО: Добавлен select_related для оптимизации
    similar_news = (
        News.objects.filter(category=news.category, is_active=True)
        .select_related("category")  # Оптимизация: загружаем категорию одним запросом
        .exclude(id=news.id)  # Исключаем текущую новость из списка похожих
        .order_by("-created_at")[:4]  # Получаем 4 последние новости из той же категории
    )

    # Последние новости для сайдбара
    # ИСПРАВЛЕНО: Используем кэш и select_related
    cache_key_sidebar = "news_sidebar_recent"
    recent_news_list = cache.get(cache_key_sidebar)
    if not recent_news_list:
        recent_news_list = list(
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:5]
        )
        cache.set(cache_key_sidebar, recent_news_list, 300)  # Кэш на 5 минут

    # Формируем данные для шаблона
    context = {
        "news": news,  # Объект новости
        "similar_news": similar_news,  # Похожие новости из той же категории
        "categories": categories,  # Список категорий для меню
        "recent_news_list": recent_news_list,  # Последние новости для сайдбара
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (news.category.name, news.category.get_absolute_url()),
            (news.title, reverse("news:detail", kwargs={"slug": news.slug})),
        ]),
    }
    return render(
        request, "news/detail.html", context
    )  # Рендерим шаблон с детальной информацией


def news_by_category(request, slug):
    """
    Отображение новостей определенной категории.
    Оптимизировано с использованием select_related и кэширования.

    Args:
        request: HTTP-запрос от пользователя
        slug: URL-дружественный идентификатор категории

    Returns:
        HttpResponse: Отрендеренный шаблон со списком новостей категории
    """
    # Получаем категорию или показываем ошибку 404
    category = get_object_or_404(NewsCategory, slug=slug, is_active=True)

    # Получаем параметры
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "-created_at")
    valid_sorts = {"created_at", "-created_at", "title", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-created_at"

    # Новости этой категории + поиск
    news_queryset = News.objects.filter(category=category, is_active=True).select_related("category")
    
    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(content__icontains=query)
        )
    
    news_queryset = news_queryset.order_by(sort_by)

    # Все активные категории для меню
    # ИСПРАВЛЕНО: Используем кэш для категорий
    cache_key = "news_categories_menu"
    categories = cache.get(cache_key)
    if not categories:
        categories = list(
            NewsCategory.objects.filter(is_active=True, show_in_menu=True).order_by(
                "order", "name"
            )
        )
        cache.set(cache_key, categories, 600)  # Кэш на 10 минут

    # Разбиваем на страницы
    paginator = Paginator(news_list, 20)  # Создаем пагинатор с 20 новостями на страницу
    page_number = request.GET.get("page", 1)  # Получаем номер страницы из GET-параметра
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы с новостями

    # Последние новости для сайдбара
    # ИСПРАВЛЕНО: Используем кэш и select_related
    cache_key_sidebar = "news_sidebar_recent"
    recent_news_list = cache.get(cache_key_sidebar)
    if not recent_news_list:
        recent_news_list = list(
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:5]
        )
        cache.set(cache_key_sidebar, recent_news_list, 300)  # Кэш на 5 минут

    # Формируем данные для шаблона
    context = {
        "category": category,
        "selected_category": category.slug,
        "news_list": page_obj,
        "categories": categories,
        "recent_news_list": recent_news_list,
        "current_sort": sort_by,
        "search_query": query,
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (category.name, category.get_absolute_url()),
        ]),
    }
    return render(
        request, "news/category.html", context
    )  # Рендерим шаблон со списком новостей категории


def news_search(request):
    """
    Поиск новостей по запросу пользователя.
    Оптимизировано с использованием select_related и кэширования.

    Args:
        request: HTTP-запрос от пользователя с параметром 'q' (поисковый запрос)

    Returns:
        HttpResponse: Отрендеренный шаблон с результатами поиска
    """
    query = request.GET.get(
        "q", ""
    )  # Получаем поисковый запрос из GET-параметра, по умолчанию пустая строка

    # ИСПРАВЛЕНО: Добавлен select_related и расширен поиск по нескольким полям
    if query:
        # Поиск по заголовку, краткому описанию и содержанию
        news_list = (
            News.objects.filter(
                Q(title__icontains=query)  # Поиск в заголовке (без учета регистра)
                | Q(short_description__icontains=query)  # Поиск в кратком описании
                | Q(content__icontains=query),  # Поиск в содержании
                is_active=True,
            )
            .select_related(
                "category"
            )  # Оптимизация: загружаем категорию одним запросом
            .distinct()  # Убираем дубликаты
            .order_by("-created_at")
        )
    else:
        # Если запрос пустой, возвращаем все активные новости
        news_list = (
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")
        )

    # Все активные категории для меню
    # ИСПРАВЛЕНО: Используем кэш для категорий
    cache_key = "news_categories_menu"
    categories = cache.get(cache_key)
    if not categories:
        categories = list(
            NewsCategory.objects.filter(is_active=True, show_in_menu=True).order_by(
                "order", "name"
            )
        )
        cache.set(cache_key, categories, 600)  # Кэш на 10 минут

    # Последние новости для сайдбара
    # ИСПРАВЛЕНО: Используем кэш и select_related
    cache_key_sidebar = "news_sidebar_recent"
    recent_news_list = cache.get(cache_key_sidebar)
    if not recent_news_list:
        recent_news_list = list(
            News.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")[:5]
        )
        cache.set(cache_key_sidebar, recent_news_list, 300)  # Кэш на 5 минут

    # Формируем данные для шаблона
    context = {
        "news_list": news_list,  # Список найденных новостей
        "categories": categories,  # Список категорий для меню
        "recent_news_list": recent_news_list,  # Последние новости для сайдбара
        "query": query,  # Поисковый запрос для отображения в шаблоне
        "breadcrumbs": get_breadcrumbs([
            ("Новости", reverse("news:list"), "fas fa-newspaper"),
            (f"Поиск: {query}" if query else "Поиск", request.path),
        ]),
    }
    return render(
        request, "news/search.html", context
    )  # Рендерим шаблон с результатами поиска


# ИСПРАВЛЕНО: Функция news_by_tag удалена, так как в модели News нет поля tags
# Если в будущем понадобятся теги, нужно будет добавить поле tags в модель News
# или использовать django-taggit для работы с тегами
