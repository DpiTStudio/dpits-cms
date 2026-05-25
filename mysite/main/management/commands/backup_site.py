# main/management/commands/backup_site.py
"""
Management command для создания полного резервного копирования сайта.

Создаёт ZIP-архив, включающий:
- Базу данных (SQLite)
- Медиа-файлы (media/)
- Статические файлы разработчика (static/)
- Python-код приложений
- Конфигурационные файлы (.env.example, requirements.txt)

Использование:
    python manage.py backup_site
    python manage.py backup_site --output /path/to/backup/dir
    python manage.py backup_site --no-static       # без static/
    python manage.py backup_site --no-media        # без media/
    python manage.py backup_site --no-code         # без Python-кода
"""

import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


# Каталоги и файлы, которые никогда не включаются в архив
ALWAYS_EXCLUDE = {
    "__pycache__",
    ".git",
    ".gitignore",
    ".env",          # секреты — не бэкапим!
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
    "*.pyc",
    "*.pyo",
    "*.log",
}

# Суффиксы файлов, которые исключаются
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".bak"}


def _should_exclude(path: Path, exclude_dirs: set) -> bool:
    """
    Проверяет, нужно ли исключить файл/папку из архива.

    Параметры:
        path: Путь к файлу или директории
        exclude_dirs: Набор дополнительных директорий для исключения

    Возвращает:
        bool: True если файл/папку нужно исключить
    """
    name = path.name
    # Проверяем имя директории/файла
    if name in ALWAYS_EXCLUDE | exclude_dirs:
        return True
    # Проверяем суффикс (расширение)
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    # Проверяем наличие имени в любом из родительских каталогов пути
    for part in path.parts:
        if part in ALWAYS_EXCLUDE | exclude_dirs:
            return True
    return False


def _add_directory_to_zip(
    zip_file: zipfile.ZipFile,
    directory: Path,
    arcname_prefix: str,
    exclude_dirs: set,
    stdout,
    style,
) -> int:
    """
    Рекурсивно добавляет все файлы из директории в ZIP-архив.

    Параметры:
        zip_file: Открытый объект ZipFile
        directory: Путь к директории для добавления
        arcname_prefix: Префикс пути внутри архива
        exclude_dirs: Набор директорий для исключения
        stdout: Поток вывода (для логирования)
        style: Объект стилей Django (для цветного вывода)

    Возвращает:
        int: Количество добавленных файлов
    """
    count = 0
    if not directory.exists():
        stdout.write(style.WARNING(f"  ⚠ Директория не найдена: {directory}"))
        return count

    for item in directory.rglob("*"):
        # Проверяем нужно ли исключить элемент
        if _should_exclude(item, exclude_dirs):
            continue
        if item.is_file():
            # Путь внутри архива: prefix/relative/path
            arcname = os.path.join(arcname_prefix, item.relative_to(directory))
            try:
                zip_file.write(item, arcname)
                count += 1
            except (OSError, PermissionError) as e:
                stdout.write(style.WARNING(f"  ⚠ Пропущен файл {item.name}: {e}"))

    return count


class Command(BaseCommand):
    """
    Django management command для создания полного бэкапа сайта.

    Собирает все ключевые части проекта (БД, медиа, код, статика)
    в один ZIP-архив с временной меткой.
    """

    help = "Создаёт полный резервный архив сайта (БД + медиа + код)"

    def add_arguments(self, parser):
        """Регистрирует аргументы командной строки."""
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Путь к директории для сохранения архива (по умолчанию: BASE_DIR/backups/)",
        )
        parser.add_argument(
            "--no-static",
            action="store_true",
            default=False,
            help="Исключить папку static/ из архива",
        )
        parser.add_argument(
            "--no-media",
            action="store_true",
            default=False,
            help="Исключить папку media/ из архива",
        )
        parser.add_argument(
            "--no-code",
            action="store_true",
            default=False,
            help="Исключить Python-код приложений из архива",
        )
        parser.add_argument(
            "--compress",
            type=int,
            default=6,
            choices=range(0, 10),
            metavar="0-9",
            help="Уровень сжатия ZIP (0=без сжатия, 9=максимум, по умолчанию: 6)",
        )

    def handle(self, *args, **options):
        """
        Основная логика команды. Создаёт ZIP-архив сайта.

        Действия:
        1. Определяет директорию для сохранения архива
        2. Создаёт ZIP-файл с временной меткой
        3. Добавляет базу данных
        4. Добавляет медиа-файлы (если не --no-media)
        5. Добавляет статические файлы (если не --no-static)
        6. Добавляет Python-код (если не --no-code)
        7. Добавляет конфигурационные файлы
        8. Выводит статистику архива
        """
        base_dir = Path(settings.BASE_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Определяем директорию вывода
        if options["output"]:
            output_dir = Path(options["output"])
        else:
            output_dir = base_dir / "backups"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Имя архива
        archive_name = f"site_backup_{timestamp}.zip"
        archive_path = output_dir / archive_name

        self.stdout.write(self.style.SUCCESS(f"\n[BACKUP] Начало создания резервной копии сайта"))
        self.stdout.write(f"   Архив: {archive_path}\n")

        compress_level = options["compress"]
        compression = zipfile.ZIP_DEFLATED if compress_level > 0 else zipfile.ZIP_STORED
        total_files = 0

        try:
            with zipfile.ZipFile(
                archive_path,
                "w",
                compression=compression,
                compresslevel=compress_level,
                allowZip64=True,
            ) as zf:

                # ── 1. База данных ────────────────────────────────────────
                self.stdout.write("  [DB] Добавляю базу данных...")
                db_config = settings.DATABASES.get("default", {})
                db_name = db_config.get("NAME")

                if db_name:
                    db_path = Path(db_name)
                    if db_path.exists():
                        zf.write(db_path, f"database/{db_path.name}")
                        total_files += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"     OK {db_path.name} ({self._human_size(db_path.stat().st_size)})")
                        )
                    else:
                        self.stdout.write(self.style.WARNING(f"     WARN: База данных не найдена: {db_path}"))
                else:
                    self.stdout.write(self.style.WARNING("     WARN: Путь к базе данных не определён"))

                # ── 2. Медиа-файлы ────────────────────────────────────────
                if not options["no_media"]:
                    self.stdout.write("  [MEDIA] Добавляю медиа-файлы (media/)...")
                    media_root = Path(settings.MEDIA_ROOT)
                    added = _add_directory_to_zip(
                        zf, media_root, "media", set(), self.stdout, self.style
                    )
                    total_files += added
                    self.stdout.write(
                        self.style.SUCCESS(f"     OK Добавлено файлов: {added}")
                    )
                else:
                    self.stdout.write(self.style.WARNING("  SKIP: media/ пропущена (--no-media)"))

                # ── 3. Статические файлы разработчика ────────────────────
                if not options["no_static"]:
                    self.stdout.write("  [STATIC] Добавляю статические файлы (static/)...")
                    static_dirs = getattr(settings, "STATICFILES_DIRS", [])
                    added = 0
                    for static_dir in static_dirs:
                        static_path = Path(static_dir)
                        added += _add_directory_to_zip(
                            zf, static_path, "static", set(), self.stdout, self.style
                        )
                    total_files += added
                    self.stdout.write(
                        self.style.SUCCESS(f"     OK Добавлено файлов: {added}")
                    )
                else:
                    self.stdout.write(self.style.WARNING("  SKIP: static/ пропущена (--no-static)"))

                # ── 4. Python-код приложений ──────────────────────────────
                if not options["no_code"]:
                    self.stdout.write("  [CODE] Добавляю Python-код приложений...")

                    # Исключаем тяжёлые/ненужные директории
                    code_exclude = {
                        "staticfiles",  # collectstatic output
                        "backups",
                        "logs",
                        ".git",
                        "node_modules",
                        "__pycache__",
                        "migrations",   # можно раскомментировать если нужны миграции
                    }

                    # Список директорий приложений (все папки в BASE_DIR)
                    app_dirs = [
                        d for d in base_dir.iterdir()
                        if d.is_dir() and d.name not in code_exclude and not d.name.startswith(".")
                    ]

                    code_files = 0
                    for app_dir in app_dirs:
                        added = _add_directory_to_zip(
                            zf, app_dir, f"code/{app_dir.name}", code_exclude, self.stdout, self.style
                        )
                        code_files += added

                    # Добавляем корневые файлы проекта
                    root_files = ["manage.py", "requirements.txt", ".env.example", ".htaccess"]
                    for fname in root_files:
                        fpath = base_dir / fname
                        if fpath.exists():
                            zf.write(fpath, f"code/{fname}")
                            code_files += 1

                    total_files += code_files
                    self.stdout.write(
                        self.style.SUCCESS(f"     OK Добавлено файлов: {code_files}")
                    )
                else:
                    self.stdout.write(self.style.WARNING("  SKIP: Код пропущен (--no-code)"))

                # ── 5. Манифест архива ────────────────────────────────────
                manifest_content = (
                    f"DPITS-CMS Site Backup\n"
                    f"======================\n"
                    f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Всего файлов: {total_files}\n"
                    f"Параметры:\n"
                    f"  - no-static: {options['no_static']}\n"
                    f"  - no-media: {options['no_media']}\n"
                    f"  - no-code: {options['no_code']}\n"
                    f"  - compress: {compress_level}\n"
                    f"\nСостав архива:\n"
                    f"  database/ - база данных SQLite\n"
                )
                if not options["no_media"]:
                    manifest_content += "  media/    - загруженные пользователями файлы\n"
                if not options["no_static"]:
                    manifest_content += "  static/   - статические файлы разработчика\n"
                if not options["no_code"]:
                    manifest_content += "  code/     - Python-код приложений\n"

                zf.writestr("MANIFEST.txt", manifest_content)

        except Exception as e:
            # Если архив не создался — удаляем неполный файл
            if archive_path.exists():
                archive_path.unlink()
            self.stdout.write(self.style.ERROR(f"\n❌ Ошибка создания архива: {e}"))
            raise

        # ── Итоговая статистика ───────────────────────────────────────────
        archive_size = archive_path.stat().st_size
        self.stdout.write(
            self.style.SUCCESS(
                f"\n[DONE] Резервная копия успешно создана!\n"
                f"   Файл:     {archive_path.name}\n"
                f"   Путь:     {archive_path}\n"
                f"   Размер:   {self._human_size(archive_size)}\n"
                f"   Файлов:   {total_files}\n"
            )
        )

        return str(archive_path)

    @staticmethod
    def _human_size(size_bytes: int) -> str:
        """Форматирует размер файла в человекочитаемый вид (KB/MB/GB)."""
        if size_bytes < 1024:
            return f"{size_bytes} Б"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} КБ"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / 1024 ** 2:.1f} МБ"
        else:
            return f"{size_bytes / 1024 ** 3:.2f} ГБ"
