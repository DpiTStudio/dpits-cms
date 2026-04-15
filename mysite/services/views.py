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
    Отображает список всех услуг и категорий.
    """
    cache_key_categories = "services_categories_active"
    categories = cache.get(cache_key_categories)
    if not categories:
        categories = list(ServiceCategory.objects.filter(is_active=True).order_by('order', 'name'))
        cache.set(cache_key_categories, categories, 600)

    # Получаем параметры
    query = request.GET.get("q", "")
    # Сортировка
    sort_by = request.GET.get("sort", "category") 
    category_slug = request.GET.get("category")
    valid_sorts = {"created_at", "-created_at", "name", "-views", "category"}
    if sort_by not in valid_sorts:
        sort_by = "category"
    
    # Фильтрация
    services_queryset = Service.objects.filter(is_displayed=True).select_related('category')
    
    if query:
        services_queryset = services_queryset.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )
        
    if category_slug:
        services_queryset = services_queryset.filter(category__slug=category_slug)
    
    # Сортировка
    if sort_by == "category":
        services_queryset = services_queryset.order_by("category__name", "name")
    elif sort_by == "title":
        services_queryset = services_queryset.order_by("name")
    else:
        services_queryset = services_queryset.order_by(sort_by)

    services = list(services_queryset)
    
    # Пересобираем categories_with_services для обратной совместимости если нужно, 
    # но мы будем использовать all_services в новом дизайне
    categories_with_services = []
    for category in categories:
        category_services = [s for s in services if s.category_id == category.id]
        if category_services:
            categories_with_services.append({
                'category': category,
                'services': category_services
            })
    
    context = {
        'categories': categories,
        'categories_with_services': categories_with_services,
        'all_services': services,
        'page_title': 'Услуги',
        'selected_category': category_slug or "",
        'current_sort': sort_by,
        'search_query': query,
        'breadcrumbs': get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
        ]),
    }
    return render(request, 'services/list.html', context)

def service_detail(request, slug):
    """
    Отображает детальную информацию об услуге.
    """
    service = get_object_or_404(
        Service.objects.select_related('category'), 
        slug=slug, 
        is_displayed=True
    )
    service.increment_views()
    
    # Похожие услуги из той же категории
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
            (service.name, reverse("services:detail", kwargs={"slug": service.slug})),
        ]),
    }
    return render(request, 'services/detail.html', context)

def service_category(request, slug):
    """
    Отображает список услуг в конкретной категории.
    """
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    # Получаем параметры
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "-created_at")
    
    valid_sorts = {"created_at", "-created_at", "name", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-created_at"
        
    services_queryset = Service.objects.filter(category=category, is_displayed=True).select_related('category')
    
    if query:
        services_queryset = services_queryset.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )
        
    services = services_queryset.order_by(sort_by if sort_by != "title" else "name")

    # Все категории для фильтра — берём из кэша
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
    Страница оформления заказа из корзины.
    Поддерживает два режима:
    - quick: быстрый заказ (QuickOrderForm)
    - full:  полный заказ (FullOrderForm)
    """
    cart = Cart(request)

    # Список элементов корзины
    cart_items = list(cart)
    if not cart_items:
        messages.warning(request, "Корзина пуста. Добавьте услуги перед оформлением заказа.")
        return redirect("services:list")

    # Определяем тип формы
    order_type = request.GET.get("type", "quick")  # quick | full
    if order_type not in ("quick", "full"):
        order_type = "quick"

    FormClass = FullOrderForm if order_type == "full" else QuickOrderForm

    # Предзаполнение данных авторизованного пользователя
    initial = {}
    if request.user.is_authenticated:
        initial["client_name"] = request.user.get_full_name() or request.user.username
        initial["client_email"] = request.user.email
        try:
            initial["client_phone"] = request.user.profile.phone or ""
        except Exception:
            pass

    if request.method == "POST" and request.POST.get("order_type") in ("quick", "full"):
        posted_type = request.POST.get("order_type")
        PostFormClass = FullOrderForm if posted_type == "full" else QuickOrderForm
        form = PostFormClass(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
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

                    # Сохраняем позиции заказа
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
        # Если форма невалидна — продолжаем отображать ошибки
        order_type = posted_type
    else:
        form = FormClass(initial=initial)

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
    Страница успешного оформления.
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