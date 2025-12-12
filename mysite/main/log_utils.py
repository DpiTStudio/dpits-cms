# log_utils.py (новый файл)
"""
УТИЛИТЫ ДЛЯ РАБОТЫ С ЛОГ-ФАЙЛАМИ

Этот файл содержит функции для анализа, очистки и сбора статистики по логам.
Основное назначение - работа с файлом debug.log в стандартной директории логов Django.

Основные функции:
1. get_log_file_path: Получение пути к лог-файлу
2. log_file_exists: Проверка существования файла
3. get_log_file_size: Получение размера файла
4. count_total_lines: Подсчет строк в файле
5. analyze_log_categories: Анализ логов по категориям
6. get_log_file_info: Полная информация о лог-файле
7. clear_log_file: Очистка лог-файла
8. get_recent_log_lines: Получение последних строк лога

Все функции используют кэширование для оптимизации производительности.
"""
import os  # Модуль для работы с файловой системой
import re  # Модуль для работы с регулярными выражениями
from datetime import datetime  # Класс для работы с датой и временем
from django.conf import settings  # Настройки Django проекта
from django.core.cache import cache  # Система кэширования Django
import logging  # Модуль логирования Python

logger = logging.getLogger(__name__)  # Создаем логгер для этого модуля


def get_log_file_path():
    """
    Получает путь к файлу debug.log.
    Проверяет стандартное расположение логов в Django проекте.
    
    Действия:
    1. Определяет директорию логов (обычно BASE_DIR/logs)
    2. Создает директорию, если она не существует
    3. Возвращает полный путь к debug.log
    
    Возвращает:
        str или None: Абсолютный путь к файлу debug.log или None при ошибке
    """
    # Стандартный путь к логам в Django
    log_dir = os.path.join(settings.BASE_DIR, "logs")
    # BASE_DIR - корневая директория проекта

    # Создаем директорию, если она не существует
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)  # Создаем директорию рекурсивно
            logger.info(f"Создана директория логов: {log_dir}")
        except Exception as e:
            logger.error(f"Ошибка создания директории логов: {e}")
            return None  # Возвращаем None при ошибке

    log_file = os.path.join(log_dir, "debug.log")  # Формируем полный путь
    return log_file


def log_file_exists():
    """
    Проверяет существование файла debug.log.
    
    Действия:
    1. Получает путь к лог-файлу
    2. Проверяет существование файла
    
    Возвращает:
        bool: True если файл существует, False в противном случае
    """
    log_file = get_log_file_path()  # Получаем путь к файлу
    if not log_file:
        return False  # Если путь None, файл не существует
    return os.path.exists(log_file)  # Проверяем существование файла


def get_log_file_size():
    """
    Получает размер лог-файла в байтах.
    
    Действия:
    1. Получает путь к лог-файлу
    2. Проверяет существование файла
    3. Возвращает размер в байтах
    
    Возвращает:
        int: Размер файла в байтах, или 0 если файл не существует
    """
    log_file = get_log_file_path()
    if not log_file or not os.path.exists(log_file):
        return 0  # Файл не существует - размер 0

    try:
        return os.path.getsize(log_file)  # Возвращаем размер файла
    except Exception as e:
        logger.error(f"Ошибка получения размера файла: {e}")
        return 0  # При ошибке возвращаем 0


def count_total_lines():
    """
    Подсчитывает общее количество строк в лог-файле.
    Использует кэширование для оптимизации производительности.
    
    Алгоритм:
    1. Проверяет наличие результата в кэше
    2. Если нет в кэше, читает файл и подсчитывает строки
    3. Сохраняет результат в кэше на 5 минут
    
    Возвращает:
        int: Общее количество строк в файле
    """
    cache_key = "log_total_lines"  # Ключ для кэша
    total_lines = cache.get(cache_key)  # Пытаемся получить из кэша

    if total_lines is not None:
        return total_lines  # Если есть в кэше, возвращаем

    log_file = get_log_file_path()
    if not log_file or not os.path.exists(log_file):
        return 0  # Файл не существует - строк 0

    total_lines = 0
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            # Быстрый подсчет строк
            for _ in f:  # Читаем файл построчно
                total_lines += 1  # Увеличиваем счетчик
        
        # Кэшируем результат на 5 минут (300 секунд)
        cache.set(cache_key, total_lines, 300)
    except Exception as e:
        logger.error(f"Ошибка подсчета строк в логе: {e}")
        total_lines = 0

    return total_lines


def analyze_log_categories():
    """
    Анализирует лог-файл и подсчитывает строки по категориям.
    Определяет категории по ключевым словам в логах.
    
    Алгоритм:
    1. Проверяет наличие результата в кэше
    2. Читает файл построчно
    3. Определяет категорию по наличию ключевых слов
    4. Подсчитывает строки каждой категории
    5. Кэширует результат на 10 минут
    
    Возвращает:
        dict: Словарь с количеством строк по категориям
    """
    cache_key = "log_categories"  # Ключ для кэша
    categories = cache.get(cache_key)  # Пытаемся получить из кэша

    if categories is not None:
        return categories  # Если есть в кэше, возвращаем

    log_file = get_log_file_path()
    if not log_file or not os.path.exists(log_file):
        return {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0, "OTHER": 0}
        # Возвращаем пустую статистику если файла нет

    # Инициализируем счетчики
    categories = {"ERROR": 0, "WARNING": 0, "INFO": 0, "DEBUG": 0, "OTHER": 0}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:  # Читаем файл построчно
                line_upper = line.upper()  # Приводим к верхнему регистру для поиска
                
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

        # Кэшируем результат на 10 минут (600 секунд)
        cache.set(cache_key, categories, 600)
    except Exception as e:
        logger.error(f"Ошибка анализа категорий логов: {e}")

    return categories


def get_log_file_info():
    """
    Получает полную информацию о лог-файле.
    Включает размер, количество строк и статистику по категориям.
    
    Действия:
    1. Проверяет существование файла
    2. Собирает всю информацию о файле
    3. Форматирует данные для удобства чтения
    
    Возвращает:
        dict: Словарь с информацией о лог-файле
    """
    log_file = get_log_file_path()

    if not log_file or not os.path.exists(log_file):
        # Возвращаем информацию о несуществующем файле
        return {
            "exists": False,  # Файл не существует
            "file_path": log_file,  # Путь к файлу
            "file_size": 0,  # Размер 0
            "file_size_human": "0 Б",  # Человекочитаемый размер
            "total_lines": 0,  # Строк 0
            "categories": {},  # Пустая статистика
            "last_modified": None,  # Дата изменения отсутствует
        }

    # Получаем информацию о файле
    file_size = get_log_file_size()  # Размер в байтах
    total_lines = count_total_lines()  # Количество строк
    categories = analyze_log_categories()  # Статистика по категориям

    # Форматируем размер файла для удобства чтения
    size_units = ["Б", "КБ", "МБ", "ГБ"]  # Единицы измерения
    size_human = file_size  # Начинаем с байтов
    unit_index = 0  # Индекс текущей единицы измерения

    # Переводим в более крупные единицы пока возможно
    while size_human >= 1024 and unit_index < len(size_units) - 1:
        size_human /= 1024  # Делим на 1024
        unit_index += 1  # Переходим к следующей единице

    # Форматируем строку с размером
    file_size_human = f"{size_human:.2f} {size_units[unit_index]}"

    # Получаем время последнего изменения
    try:
        last_modified = datetime.fromtimestamp(os.path.getmtime(log_file))
        last_modified_str = last_modified.strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        last_modified_str = None  # Если ошибка, возвращаем None

    # Возвращаем полную информацию
    return {
        "exists": True,  # Файл существует
        "file_path": log_file,  # Полный путь
        "file_size": file_size,  # Размер в байтах
        "file_size_human": file_size_human,  | Размер для отображения
        "total_lines": total_lines,  # Количество строк
        "categories": categories,  # Статистика по категориям
        "last_modified": last_modified_str,  | Дата последнего изменения
    }


def clear_log_file():
    """
    Очищает содержимое лог-файла.
    Создает резервную копию перед очисткой.
    
    Действия:
    1. Создает резервную копию файла
    2. Очищает основной файл
    3. Добавляет запись о времени очистки
    4. Очищает связанный кэш
    
    Возвращает:
        tuple: (success: bool, message: str) - результат операции
    """
    log_file = get_log_file_path()

    if not log_file or not os.path.exists(log_file):
        return False, "Лог-файл не существует"

    try:
        # Создаем резервную копию
        backup_file = f"{log_file}.backup"  | Имя файла бэкапа
        with open(log_file, "r", encoding="utf-8") as src:
            with open(backup_file, "w", encoding="utf-8") as dst:
                dst.write(src.read())  | Копируем содержимое

        # Очищаем основной файл
        with open(log_file, "w", encoding="utf-8") as f:
            # Добавляем запись о времени очистки
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
    
    Алгоритм:
    1. Читает файл с конца
    2. Находит последние N строк
    3. Возвращает их в правильном порядке
    
    Параметры:
        count (int): Количество строк для получения (по умолчанию 100)
    
    Возвращает:
        list: Список последних строк лога
    """
    log_file = get_log_file_path()

    if not log_file or not os.path.exists(log_file):
        return ["Лог-файл не существует"]  | Сообщение об отсутствии файла

    try:
        lines = []  | Список для хранения строк
        with open(log_file, "r", encoding="utf-8") as f:
            # Читаем файл с конца
            f.seek(0, 2)  # Переходим в конец файла (2 = SEEK_END)
            file_size = f.tell()  # Получаем размер файла

            buffer_size = 4096  | Размер буфера для чтения
            buffer = bytearray()  | Буфер для хранения данных
            position = file_size  | Текущая позиция в файле

            # Читаем пока не наберем нужное количество строк
            while len(lines) < count and position > 0:
                # Определяем размер для чтения
                to_read = min(buffer_size, position)
                position -= to_read  | Сдвигаем позицию назад
                f.seek(position)  | Переходим на новую позицию

                # Читаем данные
                chunk = f.read(to_read)
                # Добавляем в начало буфера
                buffer[:0] = chunk.encode() if isinstance(chunk, str) else chunk

                # Разделяем на строки
                while b"\n" in buffer:
                    line_end = buffer.rfind(b"\n")  | Ищем последний перенос строки
                    if line_end == -1:
                        break

                    # Извлекаем строку
                    line = buffer[line_end + 1 :].decode("utf-8", errors="ignore")
                    if line.strip():  | Пропускаем пустые строки
                        lines.append(line)
                        if len(lines) >= count:
                            break  | Достаточно строк

                    buffer = buffer[:line_end]  | Убираем обработанную часть

            # Добавляем оставшуюся часть
            if buffer and len(lines) < count:
                lines.append(buffer.decode("utf-8", errors="ignore"))

        # Реверсируем, чтобы получить правильный порядок (старые -> новые)
        return list(reversed(lines))
    except Exception as e:
        logger.error(f"Ошибка чтения последних строк лога: {e}")
        return [f"Ошибка чтения лога: {str(e)}"]
      