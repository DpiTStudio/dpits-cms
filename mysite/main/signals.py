# signals.py
"""
СИГНАЛЫ ДЛЯ ОЧИСТКИ КЭША ПРИ ИЗМЕНЕНИЯХ В МОДЕЛЯХ

Этот файл содержит обработчики сигналов Django, которые автоматически
очищают кэш при изменении данных в моделях.

Основные функции:
1. clear_site_settings_cache: Очищает кэш настроек сайта
2. clear_pages_cache: Очищает кэш страниц
3. clear_managed_files_cache: Очищает кэш управляемых файлов
4. clear_log_stats_cache: Очищает кэш статистики логов

Сигналы срабатывают автоматически при сохранении или удалении объектов.
Это обеспечивает актуальность данных в кэше.
"""

from django.db.models.signals import post_save, post_delete  # Сигналы Django
from django.dispatch import receiver  # Декоратор для приема сигналов
from django.core.cache import cache  # Система кэширования Django
from .models import SiteSettings, Page, LogStats  # Импорт моделей


@receiver([post_save, post_delete], sender=SiteSettings)
def clear_site_settings_cache(sender, **kwargs):
    """
    Очищает кэш настроек сайта при сохранении или удалении.
    Вызывается автоматически при изменениях в модели SiteSettings.

    Действия:
    1. Удаляет кэш настроек сайта
    2. Удаляет кэш меню страниц
    3. Удаляет кэш рекомендуемых страниц

    Параметры:
        sender: Класс модели, отправившей сигнал
        **kwargs: Дополнительные аргументы (instance, created и т.д.)
    """
    cache_keys = [
        "site_settings",  # Основные настройки сайта
        "site_settings_IndexView",  # Кэш для IndexView
        "site_settings_PageDetailView",  # Кэш для PageDetailView
        "menu_pages",  # Кэш меню навигации
        "featured_pages",  # Кэш рекомендуемых страниц
    ]
    for key in cache_keys:
        cache.delete(key)  # Удаляем каждый ключ из кэша


@receiver([post_save, post_delete], sender=Page)
def clear_pages_cache(sender, **kwargs):
    """
    Очищает кэш страниц при сохранении или удалении.
    Вызывается автоматически при изменениях в модели Page.

    Действия:
    1. Удаляет кэш меню страниц
    2. Удаляет кэш рекомендуемых страниц

    Параметры:
        sender: Класс модели, отправившей сигнал
        **kwargs: Дополнительные аргументы
    """
    cache_keys = ["menu_pages", "featured_pages"]
    for key in cache_keys:
        cache.delete(key)


@receiver([post_save, post_delete])
def clear_managed_files_cache(sender, **kwargs):
    """
    Очищает кэш при изменении управляемых файлов.

    Действия:
    1. Проверяет, что это модель ManagedFile
    2. Удаляет кэш списка файлов
    3. Удаляет кэш активных файлов
    4. Удаляет кэш статистики файлов

    Параметры:
        sender: Класс модели, отправившей сигнал
        **kwargs: Дополнительные аргументы
    """
    # Проверяем, что это модель ManagedFile
    if sender.__name__ == "ManagedFile":
        from .models import ManagedFile

        cache_keys = [
            "managed_files_list",  # Кэш списка всех файлов
            "managed_files_active",  # Кэш активных файлов
            "managed_files_stats",  # Кэш статистики файлов
        ]
        for key in cache_keys:
            cache.delete(key)


@receiver([post_save, post_delete], sender=LogStats)
def clear_log_stats_cache(sender, **kwargs):
    """
    Очищает кэш статистики логов при сохранении или удалении.
    Вызывается автоматически при изменениях в модели LogStats.

    Действия:
    1. Удаляет кэш статистики логов

    Параметры:
        sender: Класс модели, отправившей сигнал
        **kwargs: Дополнительные аргументы
    """
    cache_keys = [
        "log_stats_daily",  # Кэш дневной статистики
        "log_stats_monthly",  # Кэш месячной статистики
        "log_stats_yearly",  # Кэш годовой статистики
        "log_categories",  # Кэш категорий логов
        "log_total_lines",  # Кэш общего количества строк
    ]
    for key in cache_keys:
        cache.delete(key)
