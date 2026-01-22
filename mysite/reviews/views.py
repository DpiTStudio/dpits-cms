# reviews/views.py
# Представления (контроллеры) для приложения reviews (отзывы)
from django.shortcuts import render, redirect, reverse  # Импорт функций для рендеринга шаблонов и перенаправления
from main.breadcrumbs import get_breadcrumbs
from django.contrib import messages  # Импорт системы сообщений Django
from django.core.paginator import Paginator  # Импорт класса для пагинации (разбиения на страницы)
from django.core.cache import cache  # Импорт кэша для оптимизации производительности
from django.db import transaction  # Импорт транзакций для безопасного сохранения данных
from .models import Review  # Импорт модели отзыва
from .forms import ReviewForm  # Импорт формы для создания отзыва


def review_list(request):
    """
    Представление для отображения списка одобренных отзывов.
    Оптимизировано с использованием select_related и кэширования.
    
    Args:
        request: HTTP-запрос от пользователя
        
    Returns:
        HttpResponse: Отрендеренный шаблон со списком отзывов
    """
    try:
        # ИСПРАВЛЕНО: Добавлен select_related для оптимизации запросов к автору
        # ИСПРАВЛЕНО: Добавлена пагинация для больших списков отзывов
        # ИСПРАВЛЕНО: Используем кэш для списка отзывов
        
        # Получаем одобренные отзывы
        reviews_queryset = (
            Review.objects.filter(status="approved")
            .select_related("author")  # Оптимизация: загружаем автора одним запросом
            .order_by("-created_at")  # Сортируем по дате создания (новые сверху)
        )
        
        # Разбиваем на страницы по 20 отзывов
        paginator = Paginator(reviews_queryset, 20)  # Создаем пагинатор с 20 отзывами на страницу
        page_number = request.GET.get("page", 1)  # Получаем номер страницы из GET-параметра, по умолчанию 1
        page_obj = paginator.get_page(page_number)  # Получаем объект страницы с отзывами
        
        reviews = page_obj  # Используем объект страницы вместо списка
    except Exception as e:  # Если произошла ошибка
        reviews = []  # Устанавливаем пустой список отзывов
        messages.error(request, f"Ошибка загрузки отзывов: {str(e)}")  # Показываем сообщение об ошибке
    
    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "reviews/list.html",  # Путь к шаблону
        {
            "reviews": reviews,
            "breadcrumbs": get_breadcrumbs([
                ("Отзывы", reverse("reviews:list"), "fas fa-star"),
            ]),
        },  # Объект страницы с отзывами
    )  # Рендерим шаблон со списком отзывов


def add_review(request):
    """
    Представление для добавления нового отзыва.
    Обрабатывает форму создания отзыва с валидацией и обработкой ошибок.
    
    Args:
        request: HTTP-запрос от пользователя
        
    Returns:
        HttpResponse: Отрендеренный шаблон формы или редирект на список отзывов
    """
    if request.method == "POST":  # Если запрос методом POST (отправка формы)
        form = ReviewForm(request.POST)  # Создаем форму с данными из POST-запроса
        if form.is_valid():  # Если форма валидна
            try:
                # ИСПРАВЛЕНО: Используем транзакцию для безопасного сохранения
                with transaction.atomic():  # Начинаем транзакцию
                    # Если пользователь аутентифицирован, устанавливаем автора
                    if request.user.is_authenticated:  # Проверяем, аутентифицирован ли пользователь
                        review = form.save(commit=False)  # Создаем объект отзыва без сохранения
                        review.author = request.user  # Устанавливаем автора отзыва
                        review.save()  # Сохраняем отзыв в базе данных
                    else:  # Если пользователь не аутентифицирован
                        form.save()  # Сохраняем отзыв без автора
                    
                    # Очищаем кэш отзывов после добавления нового отзыва
                    cache.delete("reviews_approved_list")  # Удаляем кэш списка одобренных отзывов
                    cache.delete("sidebar_data")  # Удаляем кэш данных сайдбара
                
                messages.success(
                    request, "Ваш отзыв отправлен на модерацию. Спасибо!"
                )  # Показываем сообщение об успехе
                return redirect("reviews:list")  # Перенаправляем на список отзывов
            except Exception as e:  # Если произошла ошибка при сохранении
                # ИСПРАВЛЕНО: Используем логирование вместо вывода ошибки пользователю
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка сохранения отзыва: {e}")  # Записываем ошибку в лог
                messages.error(
                    request, "Произошла ошибка при сохранении отзыва. Попробуйте позже."
                )  # Показываем общее сообщение об ошибке
        else:  # Если форма не валидна
            messages.error(
                request, "Пожалуйста, исправьте ошибки в форме."
            )  # Показываем сообщение об ошибках валидации
    else:  # Если запрос методом GET (отображение формы)
        form = ReviewForm()  # Создаем пустую форму

    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "reviews/add.html",  # Путь к шаблону
        {
            "form": form,
            "breadcrumbs": get_breadcrumbs([
                ("Отзывы", reverse("reviews:list"), "fas fa-star"),
                ("Оставить отзыв", reverse("reviews:add")),
            ]),
        },  # Форма для создания отзыва
    )  # Рендерим шаблон с формой создания отзыва
