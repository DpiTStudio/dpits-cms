# main/backup_utils.py
"""
УТИЛИТЫ ДЛЯ СИСТЕМЫ РЕЗЕРВНОГО КОПИРОВАНИЯ

Вспомогательные функции для работы с архивами бэкапов.
Используются как management command так и веб-вью.

Функции:
- get_backups_dir()      : Путь к директории бэкапов
- list_backups()         : Список всех бэкапов с метаданными
- create_site_backup()   : Создание нового архива (вызывает management command)
- delete_backup()        : Удаление архива
- get_backup_path()      : Безопасное получение пути к файлу бэкапа
- human_size()           : Форматирование размера файла
"""

import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from django.conf import settings


def get_backups_dir() -> Path:
    """
    Возвращает путь к директории для хранения бэкапов.
    Создаёт директорию, если она не существует.

    Возвращает:
        Path: Путь к директории backups/
    """
    backup_dir = Path(settings.BASE_DIR) / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def human_size(size_bytes: int) -> str:
    """
    Конвертирует размер в байтах в человекочитаемый формат.

    Параметры:
        size_bytes: Размер в байтах

    Возвращает:
        str: Строка вида "1.5 МБ", "320 КБ" и т.д.
    """
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} КБ"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} МБ"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} ГБ"


def list_backups() -> list:
    """
    Возвращает список всех резервных копий в директории backups/.
    Сортирует от новых к старым.

    Возвращает:
        list[dict]: Список словарей с информацией о каждом бэкапе:
            - filename: Имя файла
            - path: Полный путь
            - size_bytes: Размер в байтах
            - size_human: Размер в читаемом виде
            - created_at: datetime создания
            - created_at_str: Строка с датой
            - type: 'full' (сайт) или 'db' (только БД)
            - is_zip: bool (является ли ZIP-архивом)
    """
    backups_dir = get_backups_dir()
    backups = []

    # Перебираем все файлы в директории бэкапов
    for filepath in backups_dir.iterdir():
        if not filepath.is_file():
            continue
        # Принимаем только .zip и .sqlite3 файлы
        if filepath.suffix not in (".zip", ".sqlite3"):
            continue

        stat = filepath.stat()
        created_at = datetime.fromtimestamp(stat.st_mtime)

        # Определяем тип бэкапа по имени и расширению
        if filepath.suffix == ".zip":
            backup_type = "full"
            is_zip = True
        else:
            backup_type = "db"
            is_zip = False

        # Проверяем целостность ZIP-архива
        is_valid = True
        if is_zip:
            try:
                with zipfile.ZipFile(filepath, "r") as zf:
                    bad = zf.testzip()
                    is_valid = bad is None
            except (zipfile.BadZipFile, Exception):
                is_valid = False

        backups.append({
            "filename": filepath.name,
            "path": str(filepath),
            "size_bytes": stat.st_size,
            "size_human": human_size(stat.st_size),
            "created_at": created_at,
            "created_at_str": created_at.strftime("%d.%m.%Y %H:%M:%S"),
            "type": backup_type,
            "is_zip": is_zip,
            "is_valid": is_valid,
        })

    # Сортировка от новых к старым
    backups.sort(key=lambda x: x["created_at"], reverse=True)
    return backups


def get_backup_path(filename: str) -> Optional[Path]:
    """
    Безопасно возвращает путь к файлу бэкапа.
    Защищает от path traversal атак — файл должен быть в backups/.

    Параметры:
        filename: Имя файла (без пути, только имя)

    Возвращает:
        Path или None если файл не найден / небезопасный путь
    """
    # Берём только basename для защиты от path traversal
    safe_name = Path(filename).name
    backups_dir = get_backups_dir()
    filepath = backups_dir / safe_name

    # Дополнительная проверка: файл должен находиться в backups/
    try:
        filepath.resolve().relative_to(backups_dir.resolve())
    except ValueError:
        return None

    if filepath.exists() and filepath.is_file():
        return filepath
    return None


def delete_backup(filename: str) -> tuple[bool, str]:
    """
    Удаляет файл бэкапа по имени.

    Параметры:
        filename: Имя файла для удаления

    Возвращает:
        tuple[bool, str]: (успех, сообщение)
    """
    filepath = get_backup_path(filename)
    if filepath is None:
        return False, f"Файл '{filename}' не найден в директории бэкапов"

    try:
        filepath.unlink()
        return True, f"Файл '{filename}' успешно удалён"
    except OSError as e:
        return False, f"Ошибка удаления файла: {e}"


def create_site_backup(
    include_media: bool = True,
    include_static: bool = True,
    include_code: bool = True,
    compress_level: int = 6,
) -> tuple[bool, str, Optional[str]]:
    """
    Создаёт полный бэкап сайта, вызывая management command в текущем процессе.

    Параметры:
        include_media: Включить медиа-файлы
        include_static: Включить статические файлы
        include_code: Включить Python-код
        compress_level: Уровень сжатия (0-9)

    Возвращает:
        tuple[bool, str, Optional[str]]: (успех, сообщение, имя_файла или None)
    """
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    err = StringIO()

    try:
        call_command(
            "backup_site",
            output=str(get_backups_dir()),
            no_static=not include_static,
            no_media=not include_media,
            no_code=not include_code,
            compress=compress_level,
            stdout=out,
            stderr=err,
        )
        output_text = out.getvalue()

        # Парсим имя файла из вывода команды
        filename = None
        for line in output_text.splitlines():
            if "Файл:" in line and ".zip" in line:
                # Строка вида: "   Файл:     site_backup_20260525_123456.zip"
                filename = line.split("Файл:")[-1].strip()
                break

        return True, "Резервная копия успешно создана", filename

    except Exception as e:
        error_text = err.getvalue()
        return False, f"Ошибка создания резервной копии: {e}\n{error_text}", None


def get_backups_stats() -> dict:
    """
    Возвращает агрегированную статистику по бэкапам.

    Возвращает:
        dict: Статистика:
            - total_count: Общее количество
            - full_count: Количество полных бэкапов (ZIP)
            - db_count: Количество бэкапов только БД
            - total_size: Суммарный размер в байтах
            - total_size_human: Суммарный размер читаемо
            - latest: Последний бэкап (dict или None)
    """
    backups = list_backups()
    total_size = sum(b["size_bytes"] for b in backups)

    return {
        "total_count": len(backups),
        "full_count": sum(1 for b in backups if b["type"] == "full"),
        "db_count": sum(1 for b in backups if b["type"] == "db"),
        "total_size": total_size,
        "total_size_human": human_size(total_size),
        "latest": backups[0] if backups else None,
    }
