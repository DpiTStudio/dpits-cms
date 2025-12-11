# log_utils.py (новый файл)
"""
Утилиты для работы с лог-файлами.
Содержит функции для анализа, очистки и сбора статистики по логам.
"""

import os
import re
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def get_log_file_path():
    """
    Получает путь к файлу debug.log.
    Проверяет стандартное расположение логов в Django проекте.

    Returns:
        str: Абсолютный путь к файлу debug.log
    """
    # Стандартный путь к логам в Django
    log_dir = os.path.join(settings.BASE_DIR, "logs")

    # Создаем директорию, если она не существует
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Создана директория логов: {log_dir}")
        except Exception as e:
            logger.error(f"Ошибка создания директории логов: {e}")
            return None

    log_file = os.path.join(log_dir, "debug.log")
    return log_file


def log_file_exists():
    """
    Проверяет существование файла debug.log.

    Returns:
        bool: True если файл существует, False в противном случае
    """
    log_file = get_log_file_path()
    if not log_file:
        return False
    return os.path.exists(log_file)


def get_log_file_size():
    """
    Получает размер лог-файла в байтах.

    Returns:
        int: Размер файла в байтах, или 0 если файл не существует
    """
    log_file = get_log_file_path()
    if not log_file or not os.path.exists(log_file):
        return 0

    try:
        return os.path.getsize(log_file)
    except Exception as e:
        logger.error(f"Ошибка получения размера файла: {e}")
        return 0


def count_total_lines():
    """
    Подсчитывает общее количество строк в лог-файле.
    Использует кэширование для оптимизации производительности.

    Returns:
        int: Общее количество строк в файле
    """
    cache_key = "log_total_lines"
    total_lines = cache.get(cache_key)

    if total_lines is not None:
        return total_lines

    log_file = get_log_file_path()
    if not log_file or not os.path.exists(log_file):
        return 0

    total_lines = 0
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            # Быстрый подсчет строк
            for _ in f:
                total_lines += 1
        # Кэшируем результат на 5 минут
        cache.set(cache_key, total_lines, 300)
    except Exception as e:
        logger.error(f"Ошибка подсчета строк в логе: {e}")
        total_lines = 0

    return total_lines


def analyze_log_categories():
    """
    Анализирует лог-файл и подсчитывает строки по категориям.
    Определяет категории по ключевым словам в логах.

    Returns:
        dict: Словарь с количеством строк по категориям
    """
    cache_key = "log_categories"
    categories = cache.get(cache_key)

    if categories is not None:
        return categories

    log_file = get_log_file_path()
    if not log_file or not os.path.exists(log_file):
        return {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0, "OTHER": 0}

    # Инициализируем счетчики
    categories = {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0, "OTHER": 0}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line_upper = line.upper()
                # Проверяем наличие ключевых слов в строке
                if "ERROR" in line_upper:
                    categories["ERROR"] += 1
                elif "WARNING" in line_upper:
                    categories["WARNING"] += 1
                elif "INFO" in line_upper:
                    categories["INFO"] += 1
                elif "DEBUG" in line_upper:
                    categories["DEBUG"] += 1
                else:
                    categories["OTHER"] += 1

        # Кэшируем результат на 10 минут
        cache.set(cache_key, categories, 600)
    except Exception as e:
        logger.error(f"Ошибка анализа категорий логов: {e}")

    return categories


def get_log_file_info():
    """
    Получает полную информацию о лог-файле.
    Включает размер, количество строк и статистику по категориям.

    Returns:
        dict: Словарь с информацией о лог-файле
    """
    log_file = get_log_file_path()

    if not log_file or not os.path.exists(log_file):
        return {
            "exists": False,
            "file_path": log_file,
            "file_size": 0,
            "file_size_human": "0 Б",
            "total_lines": 0,
            "categories": {},
            "last_modified": None,
        }

    # Получаем информацию о файле
    file_size = get_log_file_size()
    total_lines = count_total_lines()
    categories = analyze_log_categories()

    # Форматируем размер файла для удобства чтения
    size_units = ["Б", "КБ", "МБ", "ГБ"]
    size_human = file_size
    unit_index = 0

    while size_human >= 1024 and unit_index < len(size_units) - 1:
        size_human /= 1024
        unit_index += 1

    file_size_human = f"{size_human:.2f} {size_units[unit_index]}"

    # Получаем время последнего изменения
    try:
        last_modified = datetime.fromtimestamp(os.path.getmtime(log_file))
        last_modified_str = last_modified.strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        last_modified_str = None

    return {
        "exists": True,
        "file_path": log_file,
        "file_size": file_size,
        "file_size_human": file_size_human,
        "total_lines": total_lines,
        "categories": categories,
        "last_modified": last_modified_str,
    }


def clear_log_file():
    """
    Очищает содержимое лог-файла.
    Создает резервную копию перед очисткой.

    Returns:
        tuple: (success, message) - результат операции
    """
    log_file = get_log_file_path()

    if not log_file or not os.path.exists(log_file):
        return False, "Лог-файл не существует"

    try:
        # Создаем резервную копию
        backup_file = f"{log_file}.backup"
        with open(log_file, "r", encoding="utf-8") as src:
            with open(backup_file, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        # Очищаем основной файл
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Лог очищен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Очищаем кэш
        cache.delete_many(["log_total_lines", "log_categories"])

        logger.info(f"Лог-файл очищен. Резервная копия: {backup_file}")
        return True, "Лог-файл успешно очищен"
    except Exception as e:
        logger.error(f"Ошибка очистки лог-файла: {e}")
        return False, f"Ошибка при очистке: {str(e)}"


def get_recent_log_lines(count=100):
    """
    Получает последние N строк из лог-файла.

    Args:
        count (int): Количество строк для получения

    Returns:
        list: Список последних строк лога
    """
    log_file = get_log_file_path()

    if not log_file or not os.path.exists(log_file):
        return ["Лог-файл не существует"]

    try:
        lines = []
        with open(log_file, "r", encoding="utf-8") as f:
            # Читаем файл с конца
            f.seek(0, 2)  # Переходим в конец файла
            file_size = f.tell()

            buffer_size = 4096
            buffer = bytearray()
            position = file_size

            while len(lines) < count and position > 0:
                # Определяем размер для чтения
                to_read = min(buffer_size, position)
                position -= to_read
                f.seek(position)

                # Читаем данные
                chunk = f.read(to_read)
                buffer[:0] = chunk.encode() if isinstance(chunk, str) else chunk

                # Разделяем на строки
                while b"\n" in buffer:
                    line_end = buffer.rfind(b"\n")
                    if line_end == -1:
                        break

                    line = buffer[line_end + 1 :].decode("utf-8", errors="ignore")
                    if line.strip():
                        lines.append(line)
                        if len(lines) >= count:
                            break

                    buffer = buffer[:line_end]

            # Добавляем оставшуюся часть
            if buffer and len(lines) < count:
                lines.append(buffer.decode("utf-8", errors="ignore"))

        # Реверсируем, чтобы получить правильный порядок
        return list(reversed(lines))
    except Exception as e:
        logger.error(f"Ошибка чтения последних строк лога: {e}")
        return [f"Ошибка чтения лога: {str(e)}"]
