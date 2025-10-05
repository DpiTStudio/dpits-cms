# main/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SiteSettings, Page


@receiver([post_save, post_delete], sender=SiteSettings)
def clear_site_settings_cache(sender, **kwargs):
    """
    Очищает кэш настроек сайта при сохранении или удалении.
    """
    cache_keys = [
        "site_settings",
        "site_settings_IndexView",
        "site_settings_PageDetailView",
    ]
    for key in cache_keys:
        cache.delete(key)


@receiver([post_save, post_delete], sender=Page)
def clear_pages_cache(sender, **kwargs):
    """
    Очищает кэш страниц при сохранении или удалении.
    """
    cache.delete("menu_pages")
