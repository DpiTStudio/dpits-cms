# news/views.py
# Представления (контроллеры) для приложения news (новости)
from django.shortcuts import render, get_object_or_404  # Импорт функций для рендеринга шаблонов и получения объектов
from django.core.paginator import Paginator  # Импорт класса для пагинации (разбиения на страницы)
from django.core.cache import cache  # Импорт кэша для оптимизации производительности
from django.db.models import Q  # Импорт Q-объекта для сложных запросов
from .models import News, NewsCategory  # Импорт моделей новостей и категорий


def news_list(request):
    """
    Отображение списка всех активных новостей.
    Оптимизировано с использованием select_related для уменьшения количества запросов к БД.
    
    Args:
        request: HTTP-запрос от пользователя
        
    Returns:
        HttpResponse: Отрендеренный шаблон со списком новостей
    """
    # Получаем активные новости, отсортированные по дате (новые сверху)
    # ИСПРАВЛЕНО: Добавлен select_related для оптимизации запросов к категориям
    news_list = (
        News.objects.filter(is_active=True)
        .select_related("category")  # Оптимизация: загружаем категорию одним запросом
        .order_by("-created_at")
    )

    # Получаем активные категории для меню
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

    # Разбиваем на страницы по 20 новостей
    paginator = Paginator(news_list, 20)  # Создаем пагинатор с 20 новостями на страницу
    page_number = request.GET.get("page", 1)  # Получаем номер страницы из GET-параметра, по умолчанию 1
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы с новостями

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
        "news_list": page_obj,  # Объект страницы с новостями
        "categories": categories,  # Список категорий для меню
        "recent_news_list": recent_news_list,  # Последние новости для сайдбара
        "category": None,  # На главной странице категория не выбрана
    }
    return render(request, "news/list.html", context)  # Рендерим шаблон со списком новостей


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
    }
    return render(request, "news/detail.html", context)  # Рендерим шаблон с детальной информацией


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

    # Новости этой категории
    # ИСПРАВЛЕНО: Добавлен select_related для оптимизации
    news_list = (
        News.objects.filter(category=category, is_active=True)
        .select_related("category")  # Оптимизация: загружаем категорию одним запросом
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
        "category": category,  # Объект категории
        "news_list": page_obj,  # Объект страницы с новостями
        "categories": categories,  # Список категорий для меню
        "recent_news_list": recent_news_list,  # Последние новости для сайдбара
    }
    return render(request, "news/category.html", context)  # Рендерим шаблон со списком новостей категории


def news_search(request):
    """
    Поиск новостей по запросу пользователя.
    Оптимизировано с использованием select_related и кэширования.
    
    Args:
        request: HTTP-запрос от пользователя с параметром 'q' (поисковый запрос)
        
    Returns:
        HttpResponse: Отрендеренный шаблон с результатами поиска
    """
    query = request.GET.get("q", "")  # Получаем поисковый запрос из GET-параметра, по умолчанию пустая строка
    
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
            .select_related("category")  # Оптимизация: загружаем категорию одним запросом
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
    }
    return render(request, "news/search.html", context)  # Рендерим шаблон с результатами поиска


# ИСПРАВЛЕНО: Функция news_by_tag удалена, так как в модели News нет поля tags
# Если в будущем понадобятся теги, нужно будет добавить поле tags в модель News
# или использовать django-taggit для работы с тегами
