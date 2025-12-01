# signals.py
# Сигналы для очистки кэша при изменениях в моделях
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SiteSettings, Page


@receiver([post_save, post_delete], sender=SiteSettings)
def clear_site_settings_cache(sender, **kwargs):
    """
    Очищает кэш настроек сайта при сохранении или удалении.
    Вызывается автоматически при изменениях в модели SiteSettings.
    """
    cache_keys = [
        "site_settings",
        "site_settings_IndexView",
        "site_settings_PageDetailView",
        "menu_pages",
        "featured_pages",
    ]
    for key in cache_keys:
        cache.delete(key)


@receiver([post_save, post_delete], sender=Page)
def clear_pages_cache(sender, **kwargs):
    """
    Очищает кэш страниц при сохранении или удалении.
    Вызывается автоматически при изменениях в модели Page.
    """
    cache_keys = ["menu_pages", "featured_pages"]
    for key in cache_keys:
        cache.delete(key)


@receiver([post_save, post_delete])
def clear_managed_files_cache(sender, **kwargs):
    """
    Очищает кэш при изменении управляемых файлов
    """
    # Проверяем, что это модель ManagedFile
    if sender.__name__ == "ManagedFile":
        from .models import ManagedFile

        cache_keys = [
            "managed_files_list",
            "managed_files_active",
            "managed_files_stats",
        ]
        for key in cache_keys:
            cache.delete(key)
