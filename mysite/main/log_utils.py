# log_utils.py
"""
УТИЛИТЫ ДЛЯ РАБОТЫ С ЛОГ-ФАЙЛАМИ

Этот модуль предоставляет функции для работы с файлом debug.log:
- Получение информации о лог-файле
- Подсчет общего количества строк
- Подсчет строк по категориям (ERROR, WARNING, INFO, DEBUG, OTHER)
- Получение последних строк лога
- Очистка лог-файла с созданием резервной копии

Все функции подробно прокомментированы на русском языке.
"""

import os  # Модуль для работы с операционной системой (файлы, директории)
import re  # Модуль для работы с регулярными выражениями
import shutil  # Модуль для операций с файлами (копирование, перемещение)
from datetime import datetime  # Класс для работы с датой и временем
from django.conf import settings  # Настройки Django проекта
from django.utils import timezone  # Утилиты для работы с часовыми поясами
import logging  # Модуль для логирования

# Создаем объект логгера для записи ошибок в консоль
logger = logging.getLogger(__name__)


def get_log_file_path():
    """
    Получает абсолютный путь к файлу debug.log.
    
    Проверяет стандартное расположение логов в Django проекте:
    - BASE_DIR/logs/debug.log (стандартный путь)
    - Если директория не существует, создает её
    - Если файл не существует, создает пустой файл
    
    Возвращает:
        str или None: Абсолютный путь к файлу debug.log или None при ошибке
    """
    # Получаем стандартный путь к директории логов (BASE_DIR/logs)
    log_dir_standard = os.path.join(settings.BASE_DIR, "logs")
    
    # Альтернативный путь (mysite/logs) для совместимости
    log_dir_custom = os.path.join(settings.BASE_DIR, "mysite", "logs")
    
    # Определяем, какой путь использовать
    log_dir = None
    if os.path.exists(log_dir_standard):
        # Если стандартный путь существует, используем его
        log_dir = log_dir_standard
    elif os.path.exists(log_dir_custom):
        # Если альтернативный путь существует, используем его
        log_dir = log_dir_custom
    else:
        # Если ни один путь не существует, создаем стандартный
        log_dir = log_dir_standard
    
    # Создаем директорию для логов, если она не существует
    if not os.path.exists(log_dir):
        try:
            # Создаем директорию со всеми необходимыми родительскими папками
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Создана директория логов: {log_dir}")
        except Exception as e:
            # В случае ошибки логируем и возвращаем None
            logger.error(f"Ошибка создания директории логов: {e}")
            return None
    
    # Формируем полный путь к файлу debug.log
    log_file = os.path.join(log_dir, "debug.log")
    
    # Если файл не существует, создаем пустой файл
    if not os.path.exists(log_file):
        try:
            # Открываем файл в режиме записи и создаем начальную запись
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(
                    f"Лог-файл создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
            logger.info(f"Создан пустой лог-файл: {log_file}")
        except Exception as e:
            # В случае ошибки логируем и возвращаем None
            logger.error(f"Ошибка создания лог-файла: {e}")
            return None
    
    # Возвращаем полный путь к файлу
    return log_file


def count_total_lines(log_file_path=None):
    """
    Подсчитывает общее количество строк в лог-файле.
    
    Читает файл построчно и считает количество непустых строк.
    
    Параметры:
        log_file_path (str, optional): Путь к лог-файлу. 
                                      Если не указан, используется стандартный путь.
    
    Возвращает:
        int: Количество строк в файле (0 если файл не существует или пуст)
    """
    # Если путь не указан, получаем стандартный путь
    if log_file_path is None:
        log_file_path = get_log_file_path()
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return 0  # Если файла нет, возвращаем 0
    
    try:
        # Открываем файл в режиме чтения с кодировкой UTF-8
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Читаем все строки и считаем их количество
            lines = f.readlines()
            return len(lines)  # Возвращаем количество строк
    except Exception as e:
        # В случае ошибки логируем и возвращаем 0
        logger.error(f"Ошибка подсчета строк в логе: {e}")
        return 0


def count_lines_by_category(log_file_path=None):
    """
    Подсчитывает количество строк по категориям (уровням логирования).
    
    Анализирует каждую строку лога и определяет её категорию:
    - ERROR: строки содержащие [ERROR], ERROR, ошибка
    - WARNING: строки содержащие [WARNING], WARNING, предупреждение
    - INFO: строки содержащие [INFO], INFO, информация
    - DEBUG: строки содержащие [DEBUG], DEBUG, отладка
    - OTHER: все остальные строки
    
    Параметры:
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь.
    
    Возвращает:
        dict: Словарь с количеством строк по категориям:
            {
                'ERROR': int,
                'WARNING': int,
                'INFO': int,
                'DEBUG': int,
                'OTHER': int
            }
    """
    # Инициализируем счетчики для каждой категории
    categories = {
        'ERROR': 0,      # Счетчик ошибок
        'WARNING': 0,    # Счетчик предупреждений
        'INFO': 0,       # Счетчик информационных сообщений
        'DEBUG': 0,      # Счетчик отладочных сообщений
        'OTHER': 0       # Счетчик прочих сообщений
    }
    
    # Если путь не указан, получаем стандартный путь
    if log_file_path is None:
        log_file_path = get_log_file_path()
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return categories  # Если файла нет, возвращаем нулевые счетчики
    
    try:
        # Открываем файл в режиме чтения с кодировкой UTF-8
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Читаем файл построчно
            for line in f:
                # Преобразуем строку в верхний регистр для поиска без учета регистра
                line_upper = line.upper()
                
                # Проверяем наличие маркеров уровня логирования в строке
                # Используем регулярные выражения для надежного поиска
                if re.search(r'\bERROR\b|\[ERROR\]|ОШИБКА', line_upper, re.IGNORECASE):
                    # Если найдена ошибка, увеличиваем счетчик ERROR
                    categories['ERROR'] += 1
                elif re.search(r'\bWARNING\b|\[WARNING\]|ПРЕДУПРЕЖДЕНИЕ', line_upper, re.IGNORECASE):
                    # Если найдено предупреждение, увеличиваем счетчик WARNING
                    categories['WARNING'] += 1
                elif re.search(r'\bINFO\b|\[INFO\]|ИНФОРМАЦИЯ', line_upper, re.IGNORECASE):
                    # Если найдена информация, увеличиваем счетчик INFO
                    categories['INFO'] += 1
                elif re.search(r'\bDEBUG\b|\[DEBUG\]|ОТЛАДКА', line_upper, re.IGNORECASE):
                    # Если найдена отладка, увеличиваем счетчик DEBUG
                    categories['DEBUG'] += 1
                else:
                    # Если не найдено ни одного маркера, считаем строку прочей
                    categories['OTHER'] += 1
        
        # Возвращаем словарь с подсчитанными категориями
        return categories
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем нулевые счетчики
        logger.error(f"Ошибка подсчета категорий в логе: {e}")
        return categories


def get_log_file_info(log_file_path=None):
    """
    Получает полную информацию о лог-файле.
    
    Собирает метаданные файла:
    - Существование файла
    - Размер файла (в байтах и в читаемом формате)
    - Общее количество строк
    - Количество строк по категориям
    - Дата последнего изменения
    - Полный путь к файлу
    
    Параметры:
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь.
    
    Возвращает:
        dict: Словарь с информацией о файле:
            {
                'exists': bool,
                'file_path': str,
                'file_size': int,
                'file_size_human': str,
                'total_lines': int,
                'categories': dict,
                'last_modified': str или None
            }
    """
    # Если путь не указан, получаем стандартный путь
    if log_file_path is None:
        log_file_path = get_log_file_path()
    
    # Инициализируем базовую структуру данных
    info = {
        'exists': False,           # Флаг существования файла
        'file_path': log_file_path or '',  # Путь к файлу
        'file_size': 0,            # Размер файла в байтах
        'file_size_human': '0 B',  # Размер файла в читаемом формате
        'total_lines': 0,          # Общее количество строк
        'categories': {            # Счетчики по категориям
            'ERROR': 0,
            'WARNING': 0,
            'INFO': 0,
            'DEBUG': 0,
            'OTHER': 0
        },
        'last_modified': None      # Дата последнего изменения
    }
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return info  # Если файла нет, возвращаем базовую информацию
    
    try:
        # Получаем информацию о файле с помощью os.stat
        stat_info = os.stat(log_file_path)
        
        # Заполняем данные о файле
        info['exists'] = True                      # Файл существует
        info['file_size'] = stat_info.st_size      # Размер файла в байтах
        
        # Преобразуем размер в читаемый формат (KB, MB, GB)
        info['file_size_human'] = _format_file_size(stat_info.st_size)
        
        # Получаем дату последнего изменения
        mtime = datetime.fromtimestamp(stat_info.st_mtime)
        # Преобразуем в aware datetime для Django
        info['last_modified'] = timezone.make_aware(mtime)
        
        # Подсчитываем общее количество строк
        info['total_lines'] = count_total_lines(log_file_path)
        
        # Подсчитываем строки по категориям
        info['categories'] = count_lines_by_category(log_file_path)
        
        # Возвращаем полную информацию о файле
        return info
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем базовую информацию
        logger.error(f"Ошибка получения информации о логе: {e}")
        return info


def get_recent_log_lines(count=50, log_file_path=None):
    """
    Получает последние N строк из лог-файла.
    
    Читает файл и возвращает указанное количество последних строк.
    Полезно для отображения последних записей в интерфейсе.
    
    Параметры:
        count (int): Количество последних строк для возврата (по умолчанию 50)
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь.
    
    Возвращает:
        list: Список строк (последние N строк файла)
    """
    # Если путь не указан, получаем стандартный путь
    if log_file_path is None:
        log_file_path = get_log_file_path()
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return []  # Если файла нет, возвращаем пустой список
    
    try:
        # Открываем файл в режиме чтения с кодировкой UTF-8
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Читаем все строки из файла
            lines = f.readlines()
            
            # Берем последние N строк (или все, если строк меньше N)
            recent_lines = lines[-count:] if len(lines) > count else lines
            
            # Убираем символы переноса строки в конце каждой строки
            recent_lines = [line.rstrip('\n\r') for line in recent_lines]
            
            # Возвращаем список последних строк
            return recent_lines
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем пустой список
        logger.error(f"Ошибка чтения последних строк лога: {e}")
        return []


def clear_log_file(log_file_path=None, create_backup=True):
    """
    Очищает содержимое лог-файла.
    
    Перед очисткой может создать резервную копию файла.
    После очистки файл остается существующим, но становится пустым.
    
    Параметры:
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь.
        create_backup (bool): Создавать ли резервную копию перед очисткой (по умолчанию True)
    
    Возвращает:
        tuple: (success: bool, message: str)
            success - успешность операции
            message - текстовое сообщение о результате
    """
    # Если путь не указан, получаем стандартный путь
    if log_file_path is None:
        log_file_path = get_log_file_path()
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return False, "Лог-файл не найден"  # Возвращаем ошибку
    
    try:
        # Создаем резервную копию перед очисткой (если включено)
        if create_backup:
            backup_path, backup_message = _create_backup(log_file_path)
            if not backup_path:
                # Если не удалось создать бэкап, можно продолжить или прервать
                # В данном случае продолжаем, но предупреждаем
                logger.warning(f"Не удалось создать резервную копию: {backup_message}")
        
        # Очищаем файл, открывая его в режиме записи и записывая пустую строку
        with open(log_file_path, "w", encoding="utf-8") as f:
            # Записываем строку с информацией о времени очистки
            f.write(f"Лог-файл очищен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Возвращаем успешный результат
        message = "Лог-файл успешно очищен"
        if create_backup and backup_path:
            message += f". Резервная копия создана: {backup_path}"
        
        return True, message
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем ошибку
        error_message = f"Ошибка очистки лог-файла: {str(e)}"
        logger.error(error_message)
        return False, error_message


def _format_file_size(size_bytes):
    """
    Преобразует размер файла из байтов в читаемый формат.
    
    Вспомогательная функция для форматирования размера файла:
    - B (байты) - до 1024 байт
    - KB (килобайты) - до 1024 KB
    - MB (мегабайты) - до 1024 MB
    - GB (гигабайты) - до 1024 GB
    - TB (терабайты) - свыше 1024 GB
    
    Параметры:
        size_bytes (int): Размер файла в байтах
    
    Возвращает:
        str: Размер файла в читаемом формате (например, "1.45 MB")
    """
    # Если размер равен 0, возвращаем "0 B"
    if size_bytes == 0:
        return "0 B"
    
    # Список единиц измерения для преобразования
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    # Преобразуем байты в float для точных вычислений
    size = float(size_bytes)
    
    # Перебираем единицы измерения
    for unit in units:
        # Если размер меньше 1024 в текущих единицах, возвращаем результат
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        
        # Переводим в следующую единицу измерения (делим на 1024)
        size /= 1024.0
    
    # Если размер очень большой, возвращаем в терабайтах
    return f"{size:.2f} PB"  # PB = петабайты (на случай очень больших файлов)


def _create_backup(log_file_path):
    """
    Создает резервную копию лог-файла.
    
    Вспомогательная функция для создания бэкапа перед очисткой.
    Копия сохраняется в директории backups рядом с исходным файлом.
    Имя файла включает временную метку.
    
    Параметры:
        log_file_path (str): Путь к файлу для резервного копирования
    
    Возвращает:
        tuple: (backup_path: str или None, message: str)
            backup_path - путь к созданной копии или None при ошибке
            message - текстовое сообщение о результате
    """
    try:
        # Получаем директорию, где находится лог-файл
        log_dir = os.path.dirname(log_file_path)
        
        # Создаем путь к директории для бэкапов
        backup_dir = os.path.join(log_dir, "backups")
        
        # Создаем директорию для бэкапов, если её нет
        os.makedirs(backup_dir, exist_ok=True)
        
        # Получаем имя файла без пути
        file_name = os.path.basename(log_file_path)
        
        # Генерируем имя файла бэкапа с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_name}.backup_{timestamp}"
        
        # Формируем полный путь к файлу бэкапа
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Копируем файл с сохранением метаданных (права доступа, время)
        shutil.copy2(log_file_path, backup_path)
        
        # Возвращаем успешный результат
        return backup_path, "Резервная копия создана"
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем None
        error_message = f"Ошибка создания резервной копии: {str(e)}"
        logger.error(error_message)
        return None, error_message


# =============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ERROR.LOG
# =============================================================================

def get_error_log_file_path():
    """
    Получает абсолютный путь к файлу error.log.
    
    Проверяет стандартное расположение логов в Django проекте:
    - BASE_DIR/logs/error.log (стандартный путь)
    - BASE_DIR/mysite/logs/error.log (альтернативный путь)
    - Если директория не существует, создает её
    - Если файл не существует, создает пустой файл
    
    Возвращает:
        str или None: Абсолютный путь к файлу error.log или None при ошибке
    """
    # Получаем стандартный путь к директории логов (BASE_DIR/logs)
    log_dir_standard = os.path.join(settings.BASE_DIR, "logs")
    
    # Альтернативный путь (mysite/logs) для совместимости
    log_dir_custom = os.path.join(settings.BASE_DIR, "mysite", "logs")
    
    # Определяем, какой путь использовать
    log_dir = None
    if os.path.exists(log_dir_standard):
        # Если стандартный путь существует, используем его
        log_dir = log_dir_standard
    elif os.path.exists(log_dir_custom):
        # Если альтернативный путь существует, используем его
        log_dir = log_dir_custom
    else:
        # Если ни один путь не существует, создаем стандартный
        log_dir = log_dir_standard
    
    # Создаем директорию для логов, если она не существует
    if not os.path.exists(log_dir):
        try:
            # Создаем директорию со всеми необходимыми родительскими папками
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Создана директория логов: {log_dir}")
        except Exception as e:
            # В случае ошибки логируем и возвращаем None
            logger.error(f"Ошибка создания директории логов: {e}")
            return None
    
    # Формируем полный путь к файлу error.log
    log_file = os.path.join(log_dir, "error.log")
    
    # Если файл не существует, создаем пустой файл
    if not os.path.exists(log_file):
        try:
            # Открываем файл в режиме записи и создаем начальную запись
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(
                    f"Лог-файл ошибок создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
            logger.info(f"Создан пустой лог-файл ошибок: {log_file}")
        except Exception as e:
            # В случае ошибки логируем и возвращаем None
            logger.error(f"Ошибка создания лог-файла ошибок: {e}")
            return None
    
    # Возвращаем полный путь к файлу
    return log_file


def get_error_log_file_info(log_file_path=None):
    """
    Получает полную информацию о файле error.log.
    
    Собирает метаданные файла:
    - Существование файла
    - Размер файла (в байтах и в читаемом формате)
    - Общее количество строк
    - Количество строк по категориям (ERROR, WARNING, INFO, DEBUG, OTHER)
    - Дата последнего изменения
    - Полный путь к файлу
    
    Параметры:
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь к error.log.
    
    Возвращает:
        dict: Словарь с информацией о файле:
            {
                'exists': bool,
                'file_path': str,
                'file_size': int,
                'file_size_human': str,
                'total_lines': int,
                'categories': dict,
                'last_modified': str или None
            }
    """
    # Если путь не указан, получаем стандартный путь к error.log
    if log_file_path is None:
        log_file_path = get_error_log_file_path()
    
    # Инициализируем базовую структуру данных
    info = {
        'exists': False,           # Флаг существования файла
        'file_path': log_file_path or '',  # Путь к файлу
        'file_size': 0,            # Размер файла в байтах
        'file_size_human': '0 B',  # Размер файла в читаемом формате
        'total_lines': 0,          # Общее количество строк
        'categories': {            # Счетчики по категориям
            'ERROR': 0,
            'WARNING': 0,
            'INFO': 0,
            'DEBUG': 0,
            'OTHER': 0
        },
        'last_modified': None      # Дата последнего изменения
    }
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return info  # Если файла нет, возвращаем базовую информацию
    
    try:
        # Получаем информацию о файле с помощью os.stat
        stat_info = os.stat(log_file_path)
        
        # Заполняем данные о файле
        info['exists'] = True                      # Файл существует
        info['file_size'] = stat_info.st_size      # Размер файла в байтах
        
        # Преобразуем размер в читаемый формат (KB, MB, GB)
        info['file_size_human'] = _format_file_size(stat_info.st_size)
        
        # Получаем дату последнего изменения
        mtime = datetime.fromtimestamp(stat_info.st_mtime)
        # Преобразуем в aware datetime для Django
        info['last_modified'] = timezone.make_aware(mtime)
        
        # Подсчитываем общее количество строк
        info['total_lines'] = count_total_lines(log_file_path)
        
        # Подсчитываем строки по категориям
        info['categories'] = count_lines_by_category(log_file_path)
        
        # Возвращаем полную информацию о файле
        return info
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем базовую информацию
        logger.error(f"Ошибка получения информации о error.log: {e}")
        return info


def get_error_log_recent_lines(count=50, log_file_path=None):
    """
    Получает последние N строк из файла error.log.
    
    Читает файл и возвращает указанное количество последних строк.
    Полезно для отображения последних записей в интерфейсе.
    
    Параметры:
        count (int): Количество последних строк для возврата (по умолчанию 50)
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь к error.log.
    
    Возвращает:
        list: Список строк (последние N строк файла)
    """
    # Если путь не указан, получаем стандартный путь к error.log
    if log_file_path is None:
        log_file_path = get_error_log_file_path()
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return []  # Если файла нет, возвращаем пустой список
    
    try:
        # Открываем файл в режиме чтения с кодировкой UTF-8
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Читаем все строки из файла
            lines = f.readlines()
            
            # Берем последние N строк (или все, если строк меньше N)
            recent_lines = lines[-count:] if len(lines) > count else lines
            
            # Убираем символы переноса строки в конце каждой строки
            recent_lines = [line.rstrip('\n\r') for line in recent_lines]
            
            # Возвращаем список последних строк
            return recent_lines
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем пустой список
        logger.error(f"Ошибка чтения последних строк error.log: {e}")
        return []


def clear_error_log_file(log_file_path=None, create_backup=True):
    """
    Очищает содержимое файла error.log.
    
    Перед очисткой может создать резервную копию файла.
    После очистки файл остается существующим, но становится пустым.
    
    Параметры:
        log_file_path (str, optional): Путь к лог-файлу.
                                      Если не указан, используется стандартный путь к error.log.
        create_backup (bool): Создавать ли резервную копию перед очисткой (по умолчанию True)
    
    Возвращает:
        tuple: (success: bool, message: str)
            success - успешность операции
            message - текстовое сообщение о результате
    """
    # Если путь не указан, получаем стандартный путь к error.log
    if log_file_path is None:
        log_file_path = get_error_log_file_path()
    
    # Проверяем существование файла
    if not log_file_path or not os.path.exists(log_file_path):
        return False, "Лог-файл ошибок не найден"  # Возвращаем ошибку
    
    try:
        # Создаем резервную копию перед очисткой (если включено)
        if create_backup:
            backup_path, backup_message = _create_backup(log_file_path)
            if not backup_path:
                # Если не удалось создать бэкап, можно продолжить или прервать
                # В данном случае продолжаем, но предупреждаем
                logger.warning(f"Не удалось создать резервную копию: {backup_message}")
        
        # Очищаем файл, открывая его в режиме записи и записывая пустую строку
        with open(log_file_path, "w", encoding="utf-8") as f:
            # Записываем строку с информацией о времени очистки
            f.write(f"Лог-файл ошибок очищен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Возвращаем успешный результат
        message = "Лог-файл ошибок успешно очищен"
        if create_backup and backup_path:
            message += f". Резервная копия создана: {backup_path}"
        
        return True, message
    
    except Exception as e:
        # В случае ошибки логируем и возвращаем ошибку
        error_message = f"Ошибка очистки error.log: {str(e)}"
        logger.error(error_message)
        return False, error_message