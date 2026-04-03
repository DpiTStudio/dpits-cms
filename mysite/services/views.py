from django.shortcuts import render, get_object_or_404, reverse
from django.core.cache import cache
from django.db.models import Q
from main.breadcrumbs import get_breadcrumbs
from .models import Service, ServiceCategory



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