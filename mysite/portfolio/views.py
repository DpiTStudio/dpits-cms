# portfolio/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    PortfolioItem,
    PortfolioCategory,
    Client,
    Order,
    OrderMessage,
    Review,
)
from .forms import (
    OrderForm,
    OrderMessageForm,
    ReviewForm,
    ClientProfileForm,
    PortfolioSearchForm,
)


def portfolio_list(request):
    """Список работ портфолио с фильтрацией и поиском"""
    # Получаем параметры фильтрации
    category_slug = request.GET.get("category")
    search_query = request.GET.get("search")
    sort_by = request.GET.get("sort", "-project_date")

    # Базовый queryset только опубликованных работ
    portfolio_items = PortfolioItem.objects.filter(status="published")

    # Фильтрация по категории
    if category_slug:
        portfolio_items = portfolio_items.filter(category__slug=category_slug)

    # Поиск
    if search_query:
        portfolio_items = portfolio_items.filter(
            Q(title__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(technologies__icontains=search_query)
        )

    # Сортировка
    valid_sort_fields = [
        "-project_date",
        "project_date",
        "-created_at",
        "created_at",
        "-views",
        "title",
    ]
    if sort_by in valid_sort_fields:
        portfolio_items = portfolio_items.order_by(sort_by)
    else:
        portfolio_items = portfolio_items.order_by("-project_date")

    # Пагинация
    paginator = Paginator(portfolio_items, 9)  # 9 элементов на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Получаем все категории для фильтра
    categories = PortfolioCategory.objects.filter(is_active=True).annotate(
        works_count=Count("portfolioitem")
    )

    # Форма поиска
    search_form = PortfolioSearchForm(request.GET or None)

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "search_form": search_form,
        "current_category": category_slug,
        "search_query": search_query,
        "sort_by": sort_by,
        "total_count": portfolio_items.count(),
    }

    return render(request, "portfolio/list.html", context)


def portfolio_detail(request, slug):
    """Детальная страница работы портфолио"""
    # Получаем объект или 404
    item = get_object_or_404(
        PortfolioItem.objects.select_related("category", "client").prefetch_related(
            "review_set"
        ),
        slug=slug,
        status="published",
    )

    # Увеличиваем счетчик просмотров
    item.views += 1
    item.save(update_fields=["views"])

    # Получаем похожие работы из той же категории
    similar_items = PortfolioItem.objects.filter(
        category=item.category, status="published"
    ).exclude(id=item.id)[:3]

    # Получаем одобренные отзывы для этой работы
    reviews = Review.objects.filter(
        portfolio_item=item, is_approved=True
    ).select_related("client__user")

    context = {
        "item": item,
        "similar_items": similar_items,
        "reviews": reviews,
    }

    return render(request, "portfolio/detail.html", context)


@login_required
def create_order(request):
    """Создание нового заказа"""
    # Проверяем, есть ли у пользователя профиль клиента
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(
            request, "У вас нет профиля клиента. Пожалуйста, заполните профиль."
        )
        return redirect("portfolio:client_profile")

    if request.method == "POST":
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client
            order.save()

            messages.success(
                request, "Заказ успешно создан! Мы свяжемся с вами в ближайшее время."
            )
            return redirect("portfolio:order_detail", pk=order.pk)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = OrderForm()

    context = {"form": form, "title": "Создание заказа"}

    return render(request, "portfolio/create_order.html", context)


@login_required
def order_detail(request, pk):
    """Детальная страница заказа"""
    # Получаем заказ или 404
    order = get_object_or_404(Order.objects.select_related("client__user"), pk=pk)

    # Проверяем права доступа
    if order.client.user != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет доступа к этому заказу.")
        return redirect("portfolio:order_list")

    # Получаем сообщения заказа
    order_messages = order.messages.select_related("user").all()

    if request.method == "POST":
        form = OrderMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.order = order
            message.user = request.user
            message.is_admin_message = request.user.is_staff
            message.save()

            # Обновляем время заказа
            order.updated_at = timezone.now()
            order.save(update_fields=["updated_at"])

            messages.success(request, "Сообщение успешно отправлено!")
            return redirect("portfolio:order_detail", pk=order.pk)
    else:
        form = OrderMessageForm()

    context = {
        "order": order,
        "messages": order_messages,
        "form": form,
    }

    return render(request, "portfolio/order_detail.html", context)


@login_required
def order_list(request):
    """Список заказов пользователя"""
    try:
        client = request.user.client
        orders = Order.objects.filter(client=client).order_by("-created_at")
    except Client.DoesNotExist:
        orders = Order.objects.none()
        messages.info(request, "У вас пока нет заказов.")

    context = {
        "orders": orders,
    }

    return render(request, "portfolio/order_list.html", context)


@login_required
def client_dashboard(request):
    """Дашборд клиента"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "Пожалуйста, заполните профиль клиента.")
        return redirect("portfolio:client_profile")

    # Статистика заказов
    orders = Order.objects.filter(client=client)
    total_orders = orders.count()
    active_orders = orders.filter(status__in=["new", "in_progress"]).count()
    completed_orders = orders.filter(status="completed").count()

    # Последние заказы
    recent_orders = orders[:5]

    context = {
        "client": client,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "recent_orders": recent_orders,
    }

    return render(request, "portfolio/client_dashboard.html", context)


@login_required
def client_profile(request):
    """Профиль клиента"""
    try:
        client = request.user.client
    except Client.DoesNotExist:
        client = None

    if request.method == "POST":
        form = ClientProfileForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            client_profile = form.save(commit=False)
            if not client:
                client_profile.user = request.user
            client_profile.save()

            messages.success(request, "Профиль успешно обновлен!")
            return redirect("portfolio:client_profile")
    else:
        form = ClientProfileForm(instance=client)

    context = {
        "form": form,
        "client": client,
    }

    return render(request, "portfolio/client_profile.html", context)


@login_required
def create_review(request, slug):
    """Создание отзыва для работы портфолио"""
    portfolio_item = get_object_or_404(PortfolioItem, slug=slug, status="published")

    # Проверяем, есть ли у пользователя профиль клиента
    try:
        client = request.user.client
    except Client.DoesNotExist:
        messages.error(request, "У вас нет профиля клиента для оставления отзывов.")
        return redirect("portfolio:client_profile")

    # Проверяем, не оставлял ли уже пользователь отзыв для этой работы
    existing_review = Review.objects.filter(
        client=client, portfolio_item=portfolio_item
    ).first()
    if existing_review:
        messages.info(request, "Вы уже оставляли отзыв для этой работы.")
        return redirect("portfolio:detail", slug=slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = client
            review.portfolio_item = portfolio_item
            review.save()

            messages.success(
                request, "Отзыв успешно отправлен! Он появится после модерации."
            )
            return redirect("portfolio:detail", slug=slug)
    else:
        form = ReviewForm()

    context = {
        "form": form,
        "portfolio_item": portfolio_item,
    }

    return render(request, "portfolio/create_review.html", context)


def portfolio_categories(request):
    """Страница с категориями портфолио"""
    categories = (
        PortfolioCategory.objects.filter(is_active=True)
        .annotate(works_count=Count("portfolioitem"))
        .order_by("-order", "name")
    )

    context = {
        "categories": categories,
    }

    return render(request, "portfolio/categories.html", context)


# API views для AJAX запросов
def api_portfolio_items(request):
    """API для получения работ портфолио (для AJAX)"""
    category_slug = request.GET.get("category")
    limit = int(request.GET.get("limit", 6))

    items = PortfolioItem.objects.filter(status="published")

    if category_slug:
        items = items.filter(category__slug=category_slug)

    items = items.select_related("category")[:limit]

    data = {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "image_url": item.image.url,
                "short_description": item.short_description,
                "category_name": item.category.name,
                "project_date": item.project_date.strftime("%d.%m.%Y"),
                "url": item.get_absolute_url(),
            }
            for item in items
        ]
    }

    return JsonResponse(data)
