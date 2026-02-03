"""
Скрипт для проверки статуса site_closed
"""
import os
import django

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SiteSettings
from django.core.cache import cache

# Получаем настройки сайта
site_settings = SiteSettings.load()

print("=" * 60)
print("ПРОВЕРКА СТАТУСА САЙТА")
print("=" * 60)
print(f"Сайт закрыт (site_closed): {site_settings.site_closed}")
print(f"Сообщение при закрытии: {site_settings.closure_message[:100] if site_settings.closure_message else 'Не указано'}")
print("=" * 60)

# Проверяем кэш
cached_settings = cache.get('site_settings')
if cached_settings:
    print(f"В кэше найдены настройки: site_closed = {cached_settings.site_closed}")
else:
    print("Настройки не найдены в кэше")

print("=" * 60)
print("\nДля изменения статуса:")
print("1. Откройте админ-панель: http://127.0.0.1:6678/admin/")
print("2. Перейдите в 'Настройки сайта'")
print("3. Снимите галочку 'Сайт закрыт'")
print("4. Сохраните изменения")
print("\nКэш будет очищен автоматически при сохранении!")
