# services/views.py
# Назначение: Контроллеры (views) для обработки HTTP-запросов.
# Отвечают за отображение страниц услуг, категорий, оформление заказа.

from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.core.cache import cache
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from main.breadcrumbs import get_breadcrumbs
from .models import Service, ServiceCategory, ServiceOrder, ServiceOrderItem
from .cart import Cart
from .forms import QuickOrderForm, FullOrderForm


def service_list(request):
    """
    Отображает страницу со списком всех услуг и категорий.
    Поддерживает:
    - Поиск (параметр q)
    - Сортировку (параметр sort)
    - Фильтр по категории (параметр category)
    """
    # Кэшируем список активных категорий (на 10 минут)
    cache_key_categories = "services_categories_active"
    categories = cache.get(cache_key_categories)
    if not categories:
        categories = list(ServiceCategory.objects.filter(is_active=True).order_by('order', 'name'))
        cache.set(cache_key_categories, categories, 600)

    # Получаем параметры из GET-запроса
    query = request.GET.get("q", "")                 # Поисковый запрос
    sort_by = request.GET.get("sort", "category")    # Поле сортировки
    category_slug = request.GET.get("category")      # Фильтр по категории

    # Валидация сортировки (только разрешённые поля)
    valid_sorts = {"created_at", "-created_at", "name", "-views", "category"}
    if sort_by not in valid_sorts:
        sort_by = "category"

    # Базовый QuerySet: только отображаемые услуги, подгружаем категорию (select_related)
    services_queryset = Service.objects.filter(is_displayed=True).select_related('category')

    # Поиск по названию и описаниям
    if query:
        services_queryset = services_queryset.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )

    # Фильтр по категории
    if category_slug:
        services_queryset = services_queryset.filter(category__slug=category_slug)

    # Применяем сортировку
    if sort_by == "category":
        services_queryset = services_queryset.order_by("category__name", "name")
    elif sort_by == "name":  # Добавляем сортировку по имени (title)
        services_queryset = services_queryset.order_by("name")
    else:
        services_queryset = services_queryset.order_by(sort_by)

    services = list(services_queryset)

    # Формируем структуру категорий с услугами (для обратной совместимости с шаблонами)
    categories_with_services = []
    for category in categories:
        category_services = [s for s in services if s.category_id == category.id]
        if category_services:
            categories_with_services.append({
                'category': category,
                'services': category_services
            })

    context = {
        'categories': categories,                               # Все активные категории
        'categories_with_services': categories_with_services, # Категории с услугами
        'all_services': services,                              # Все услуги (плоский список)
        'page_title': 'Услуги',
        'selected_category': category_slug or "",
        'current_sort': sort_by,
        'search_query': query,
        'breadcrumbs': get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
        ]),
    }
    return render(request, 'services/list.html', context)


def service_detail(request, service_slug):  # ИСПРАВЛЕНО: переименован параметр из slug в service_slug
    """
    Отображает детальную страницу услуги.
    Увеличивает счётчик просмотров.
    Показывает похожие услуги из той же категории.
    """
    service = get_object_or_404(
        Service.objects.select_related('category'),
        slug=service_slug,  # Используем переименованный параметр
        is_displayed=True
    )
    service.increment_views()  # Атомарно увеличиваем просмотры

    # Похожие услуги (до 3 штук, из той же категории, исключая текущую)
    related_services = Service.objects.filter(
        category=service.category,
        is_displayed=True
    ).exclude(id=service.id).select_related('category')[:3]

    context = {
        'service': service,
        'related_services': related_services,
        'page_title': service.name,
        'meta_description': service.seo_description or service.short_description,
        'meta_keywords': service.seo_keywords,
        'breadcrumbs': get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
            (service.category.name, reverse("services:category", kwargs={"slug": service.category.slug})),
            (service.name, reverse("services:detail", kwargs={"service_slug": service.slug})),  # ИСПРАВЛЕНО
        ]),
    }
    return render(request, 'services/detail.html', context)


def service_category(request, slug):
    """
    Отображает список услуг в конкретной категории.
    Поддерживает поиск и сортировку.
    """
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)

    # Параметры фильтрации
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "-created_at")

    valid_sorts = {"created_at", "-created_at", "name", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-created_at"

    services_queryset = Service.objects.filter(category=category, is_displayed=True).select_related('category')

    # Поиск
    if query:
        services_queryset = services_queryset.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )

    # Сортировка
    services = services_queryset.order_by(sort_by if sort_by != "name" else "name")

    # Все категории для бокового меню (из кэша)
    cache_key_categories = "services_categories_active"
    categories = cache.get(cache_key_categories)
    if not categories:
        categories = list(ServiceCategory.objects.filter(is_active=True).order_by('order', 'name'))
        cache.set(cache_key_categories, categories, 600)

    context = {
        'category': category,
        'selected_category': category.slug,
        'services': services,
        'categories': categories,
        'page_title': category.name,
        'current_sort': sort_by,
        'search_query': query,
        'meta_description': category.seo_description or category.description,
        'meta_keywords': category.seo_keywords,
        'breadcrumbs': get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
            (category.name, reverse("services:category", kwargs={"slug": category.slug})),
        ]),
    }
    return render(request, 'services/category.html', context)


def checkout(request):
    """
    Страница оформления заказа.
    Поддерживает два типа форм:
    - quick (быстрый заказ): только имя, email, телефон (необязательно), комментарий
    - full (полный заказ): расширенная форма с бюджетом, сроками, источником
    """
    cart = Cart(request)
    cart_items = list(cart)

    # Проверка: корзина не должна быть пустой
    if not cart_items:
        messages.warning(request, "Корзина пуста. Добавьте услуги перед оформлением заказа.")
        return redirect("services:list")

    # Определяем тип заказа из GET или POST
    order_type = request.GET.get("type", "quick")
    if order_type not in ("quick", "full"):
        order_type = "quick"

    FormClass = FullOrderForm if order_type == "full" else QuickOrderForm

    # Предзаполнение данных для авторизованного пользователя
    initial = {}
    if request.user.is_authenticated:
        initial["client_name"] = request.user.get_full_name() or request.user.username
        initial["client_email"] = request.user.email
        # Пытаемся получить телефон из профиля (если есть)
        try:
            initial["client_phone"] = request.user.profile.phone or ""
        except Exception:
            pass  # Профиля нет или нет поля phone

    # Обработка POST-запроса (отправка формы)
    if request.method == "POST" and request.POST.get("order_type") in ("quick", "full"):
        posted_type = request.POST.get("order_type")
        PostFormClass = FullOrderForm if posted_type == "full" else QuickOrderForm
        form = PostFormClass(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():  # Гарантия целостности БД
                    # Создаём заказ
                    order = ServiceOrder(
                        user=request.user if request.user.is_authenticated else None,
                        client_name=data["client_name"],
                        client_email=data["client_email"],
                        client_phone=data.get("client_phone", ""),
                        comment=data.get("comment", ""),
                        order_type=posted_type,
                        total_price=cart.get_total_price(),
                    )
                    order.save()

                    # Сохраняем позиции заказа (заморозка цены и названия)
                    for item in cart_items:
                        ServiceOrderItem.objects.create(
                            order=order,
                            service=item.get("service"),
                            service_name=item["name"],
                            price=item["price"],
                            quantity=item["quantity"],
                        )

                    # Очищаем корзину
                    cart.clear()

                messages.success(
                    request,
                    f"✅ Заказ #{order.id} успешно оформлен! Мы свяжемся с вами в ближайшее время."
                )
                return redirect("services:order_success", pk=order.pk)

            except Exception as e:
                messages.error(request, f"Ошибка при оформлении заказа: {e}")
        else:
            # Если форма невалидна, продолжаем отображать страницу с ошибками
            order_type = posted_type
    else:
        # GET-запрос: показываем пустую форму с предзаполнением
        form = FormClass(initial=initial)

    # Контекст для шаблона
    context = {
        "cart": cart,
        "cart_items": cart_items,
        "form": form,
        "order_type": order_type,
        "quick_form": QuickOrderForm(initial=initial) if order_type == "full" else form,
        "full_form": FullOrderForm(initial=initial) if order_type == "quick" else form,
        "page_title": "Оформление заказа",
        "breadcrumbs": get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
            ("Оформление заказа", None, "fas fa-receipt"),
        ]),
    }
    return render(request, "services/checkout.html", context)


def order_success(request, pk):
    """
    Страница, показываемая после успешного оформления заказа.
    Отображает информацию о заказе.
    """
    order = get_object_or_404(ServiceOrder.objects.prefetch_related("items"), pk=pk)
    context = {
        "order": order,
        "page_title": f"Заказ #{order.id} подтверждён",
        "breadcrumbs": get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
            (f"Заказ #{order.id}", None, "fas fa-check-circle"),
        ]),
    }
    return render(request, "services/order_success.html", context)