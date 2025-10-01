# main/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import SiteSettings, Page
from django.shortcuts import render


def index_view(request):
    return render(request, "index.html", context)


def index(request):
    # Получаем настройки сайта
    site_settings = SiteSettings.load()
    settings = SiteSettings.objects.first()
    if settings and settings.site_closed:
        return render(request, "main/site_closed.html", {"settings": settings})
    # Получаем главную страницу (или нужную вам страницу)
    # Например, по slug 'home' или первую активную страницу
    try:
        page = Page.objects.filter(show_on_site=True).first()
    except Page.DoesNotExist:
        page = None

    context = {
        "site_settings": site_settings,
        "page": page,
    }
    return render(request, "main/index.html", context)


def page_detail(request, slug):
    settings = SiteSettings.objects.first()
    if settings and settings.site_closed:
        return render(request, "main/site_closed.html", {"settings": settings})

    page = get_object_or_404(Page, slug=slug, show_on_site=True)
    return render(request, "main/page_detail.html", {"page": page})
