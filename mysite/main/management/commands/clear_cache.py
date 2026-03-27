# main/management/commands/clear_cache.py
# Management command для очистки кэша приложения
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = "Очищает весь кэш приложения (Redis или LocMemCache)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keys",
            nargs="*",
            help="Конкретные ключи для удаления (если не указаны — очищается весь кэш)",
        )

    def handle(self, *args, **options):
        keys = options.get("keys")

        if keys:
            for key in keys:
                cache.delete(key)
                self.stdout.write(self.style.SUCCESS(f"✓ Удалён ключ: {key}"))
        else:
            # Известные ключи кэша проекта
            known_keys = [
                "news_categories_menu",
                "news_sidebar_recent",
                "sidebar_data",
                "dynamic_menus_data",
                "menu_pages",
                "site_settings",
            ]
            for key in known_keys:
                cache.delete(key)
                self.stdout.write(self.style.SUCCESS(f"✓ Удалён ключ: {key}"))

            # Попытка полной очистки (работает если бэкенд поддерживает)
            try:
                cache.clear()
                self.stdout.write(self.style.SUCCESS("✓ Кэш полностью очищен (cache.clear())"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠ cache.clear() не поддерживается: {e}"))

        self.stdout.write(self.style.SUCCESS("Готово!"))
