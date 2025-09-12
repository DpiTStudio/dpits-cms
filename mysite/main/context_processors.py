# main/context_processors.py

from .models import SiteSettings, Page


def site_settings(request):
    settings = SiteSettings.objects.first()
    return {"site_settings": settings}


def menu_items(request):
    pages = Page.objects.filter(show_in_menu=True, show_on_site=True).order_by("order")
    return {"menu_pages": pages}
