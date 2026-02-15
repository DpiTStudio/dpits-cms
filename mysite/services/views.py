from django.shortcuts import render, get_object_or_404, reverse
from django.core.cache import cache
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

    cache_key_services = "services_list_active"
    services = cache.get(cache_key_services)
    if not services:
        services = list(Service.objects.filter(is_displayed=True)
                       .select_related('category')
                       .order_by('category__order', 'category__name', 'name'))
        cache.set(cache_key_services, services, 600)
    
    # Создаем структуру данных для шаблона
    categories_with_services = []
    for category in categories:
        category_services = [s for s in services if s.category_id == category.id]
        if category_services:  # Показываем только категории с услугами
            categories_with_services.append({
                'category': category,
                'services': category_services
            })
    
    context = {
        'categories_with_services': categories_with_services,
        'all_services': services,  # Все услуги для отображения в "Все услуги"
        'page_title': 'Услуги',
        'category': None,
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
    services = Service.objects.filter(category=category, is_displayed=True).select_related('category')
    
    context = {
        'category': category,
        'services': services,
        'page_title': category.name,
        'meta_description': category.seo_description or category.description,
        'meta_keywords': category.seo_keywords,
        'breadcrumbs': get_breadcrumbs([
            ("Услуги", reverse("services:list"), "fas fa-concierge-bell"),
            (category.name, reverse("services:category", kwargs={"slug": category.slug})),
        ]),
    }
    return render(request, 'services/category.html', context)