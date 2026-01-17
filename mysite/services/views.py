from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory

def service_list(request):
    """
    Отображает список всех услуг и категорий.
    """
    categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')
    services = Service.objects.filter(is_displayed=True).select_related('category').order_by('category__order', 'category__name', 'name')
    
    context = {
        'categories': categories,
        'services': services,
        'page_title': 'Услуги',
    }
    return render(request, 'services/list.html', context)

def service_detail(request, slug):
    """
    Отображает детальную информацию об услуге.
    """
    service = get_object_or_404(Service, slug=slug, is_displayed=True)
    service.increment_views()
    
    # Похожие услуги из той же категории
    related_services = Service.objects.filter(
        category=service.category, 
        is_displayed=True
    ).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
        'page_title': service.name,
        'meta_description': service.seo_description or service.short_description,
        'meta_keywords': service.seo_keywords,
    }
    return render(request, 'services/detail.html', context)

def service_category(request, slug):
    """
    Отображает список услуг в конкретной категории.
    """
    category = get_object_or_404(ServiceCategory, slug=slug, is_active=True)
    services = Service.objects.filter(category=category, is_displayed=True)
    
    context = {
        'category': category,
        'services': services,
        'page_title': category.name,
        'meta_description': category.seo_description or category.description,
        'meta_keywords': category.seo_keywords,
    }
    return render(request, 'services/category.html', context)
