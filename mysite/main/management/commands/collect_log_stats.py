# management/commands/collect_log_stats.py (новый файл)
"""
Команда Django для сбора статистики лог-файлов.
Позволяет автоматически собирать статистику по логам.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import LogStats
from main.log_utils import get_log_file_info, count_total_lines, analyze_log_categories
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Команда для сбора статистики лог-файлов.
    Выполняет анализ логов и сохраняет статистику в БД.
    """

    help = "Собирает статистику лог-файлов и сохраняет в базу данных"

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки.
        """
        parser.add_argument(
            "--date", type=str, help="Дата для сбора статистики (формат: YYYY-MM-DD)"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Принудительное обновление существующей записи",
        )

    def handle(self, *args, **options):
        """
        Основной обработчик команды.
        """
        # Получаем дату для сбора статистики
        if options["date"]:
            try:
                log_date = timezone.datetime.strptime(
                    options["date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                self.stderr.write(
                    f"Неверный формат даты: {options['date']}. Используйте YYYY-MM-DD"
                )
                return
        else:
            log_date = timezone.now().date()

        self.stdout.write(f"Сбор статистики логов за {log_date}...")

        # Проверяем существование лог-файла
        log_info = get_log_file_info()
        if not log_info["exists"]:
            self.stderr.write("Лог-файл не найден")
            return

        # Проверяем, существует ли уже запись за эту дату
        existing_stat = LogStats.objects.filter(log_date=log_date).first()
        if existing_stat and not options["force"]:
            self.stdout.write(
                f"Статистика за {log_date} уже существует. Используйте --force для обновления."
            )
            return

        # Собираем статистику
        total_lines = count_total_lines()
        categories = analyze_log_categories()

        # Создаем или обновляем запись
        if existing_stat:
            stat = existing_stat
            action = "Обновлено"
        else:
            stat = LogStats(log_date=log_date)
            action = "Создано"

        stat.total_lines = total_lines
        stat.error_count = categories.get("ERROR", 0)
        stat.warning_count = categories.get("WARNING", 0)
        stat.info_count = categories.get("INFO", 0)
        stat.debug_count = categories.get("DEBUG", 0)
        stat.other_count = categories.get("OTHER", 0)

        stat.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"{action} статистика логов за {log_date}: {total_lines} строк"
            )
        )

        # Выводим детали
        self.stdout.write(f"  Ошибки: {stat.error_count}")
        self.stdout.write(f"  Предупреждения: {stat.warning_count}")
        self.stdout.write(f"  Информационные: {stat.info_count}")
        self.stdout.write(f"  Отладочные: {stat.debug_count}")
        self.stdout.write(f"  Прочие: {stat.other_count}")
