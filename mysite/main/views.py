# main/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import SiteSettings, Page


def index(request):
    settings = SiteSettings.objects.first()
    if settings and settings.site_closed:
        return render(request, "main/site_closed.html", {"settings": settings})

    return render(request, "main/index.html")


def page_detail(request, slug):
    settings = SiteSettings.objects.first()
    if settings and settings.site_closed:
        return render(request, "main/site_closed.html", {"settings": settings})

    page = get_object_or_404(Page, slug=slug, show_on_site=True)
    return render(request, "main/page_detail.html", {"page": page})
