# mysite/main/management/commands/add_debug_log.py (исправленная версия)

import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import ManagedFile


class Command(BaseCommand):
    help = "Добавляет файл debug.log в управляемые файлы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            help="Путь к файлу debug.log (по умолчанию: mysite/logs/debug.log)",
        )

    def handle(self, *args, **options):
        # Определяем путь к файлу
        if options["path"]:
            log_path = options["path"]
        else:
            # Исправленный путь
            log_path = os.path.join(settings.BASE_DIR, "logs", "debug.log")

        log_path = os.path.normpath(log_path)

        self.stdout.write(f"Путь к файлу: {log_path}")

        # Создаем директорию, если ее нет
        log_dir = os.path.dirname(log_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Создаем файл, если его нет
        if not os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"# Лог-файл приложения\n")
                f.write(f"# Создан: {self.get_current_time()}\n")

            self.stdout.write(self.style.SUCCESS(f"✅ Создан файл: {log_path}"))
        else:
            self.stdout.write(f"✅ Файл уже существует: {log_path}")

        # Проверяем, не добавлен ли уже файл
        if not ManagedFile.objects.filter(file_path=log_path).exists():
            try:
                # Создаем объект ManagedFile БЕЗ сохранения
                managed_file = ManagedFile(
                    name="debug.log",
                    file_path=log_path,
                    category="log",
                    description="Лог-файл отладки приложения",
                    is_active=True,
                    auto_backup=True,
                    max_backups=10,
                    encoding="utf-8",
                )

                # Сначала сохраняем объект
                managed_file.save()

                # Затем обновляем информацию о файле
                # (это создаст недостающие поля)
                success, message = managed_file.refresh_file_info()

                if success:
                    self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ {message}"))

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Файл успешно добавлен в управляемые файлы (ID: {managed_file.pk})"
                    )
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Ошибка: {e}"))
                # Показываем более подробную информацию об ошибке
                import traceback

                self.stdout.write(self.style.ERROR(traceback.format_exc()))
        else:
            existing_file = ManagedFile.objects.get(file_path=log_path)
            self.stdout.write(
                self.style.WARNING(f"⚠️ Файл уже добавлен (ID: {existing_file.pk})")
            )

            # Обновляем информацию
            existing_file.refresh_file_info()

    def get_current_time(self):
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
