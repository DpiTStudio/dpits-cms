# log_utils.py
# МОДУЛЬ УТИЛИТ ДЛЯ РАБОТЫ С ЛОГ-ФАЙЛАМИ
#
# Этот файл содержит набор инструментов для анализа, просмотра и управления файлами журналов (логов).
# Поддерживает работу с debug.log и error.log.

import os  # Модуль для работы с файловой системой
import shutil  # Модуль для копирования и перемещения файлов
from datetime import datetime  # Работа с датами
from django.conf import settings  # Глобальные настройки системы
from django.utils import timezone  # Учет часовых поясов системы
import logging  # Стандартная библиотека логирования Python

# Создаем объект логгера для фиксации ошибок работы самого модуля
logger = logging.getLogger(__name__)


def get_log_file_path():
    """
    Возвращает абсолютный путь к основному файлу логов debug.log.
    Если файла или папки нет, они будут созданы.
    """
    # Путь к папке logs в корне проекта
    log_dir = os.path.join(settings.BASE_DIR, "logs")
    
    # Создаем папку, если её нет
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Не удалось создать папку логов: {e}")
            return None
    
    log_file = os.path.join(log_dir, "debug.log")
    
    # Если файла нет, создаем пустой файл с начальной записью
    if not os.path.exists(log_file):
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"--- Лог создан {datetime.now()} ---\n")
        except Exception as e:
            logger.error(f"Не удалось создать файл логов: {e}")
            return None
            
    return log_file


def get_error_log_file_path():
    """
    Возвращает абсолютный путь к файлу логов ошибок error.log.
    """
    log_dir = os.path.join(settings.BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "error.log")
    if not os.path.exists(log_file):
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"--- Лог ошибок создан {datetime.now()} ---\n")
        except Exception:
            return None
            
    return log_file


def count_total_lines(log_file_path=None):
    """
    Подсчитывает общее количество строк в файле без загрузки всего файла в память.
    Эффективно для очень больших файлов.
    """
    if log_file_path is None:
        log_file_path = get_log_file_path()
        
    if not log_file_path or not os.path.exists(log_file_path):
        return 0
        
    count = 0
    try:
        # Открываем файл и считаем строки итеративно
        with open(log_file_path, "rb") as f:
            for _ in f:
                count += 1
    except Exception as e:
        logger.error(f"Ошибка при подсчете строк: {e}")
        
    return count


def count_lines_by_category(log_file_path=None):
    """
    Анализирует лог и распределяет строки по категориям (ERROR, WARNING, INFO, DEBUG).
    Использует регулярные выражения для поиска меток уровней.
    """
    if log_file_path is None:
        log_file_path = get_log_file_path()
        
    stats = {
        'ERROR': 0,
        'WARNING': 0,
        'INFO': 0,
        'DEBUG': 0,
        'OTHER': 0
    }
    
    if not log_file_path or not os.path.exists(log_file_path):
        return stats
        
    try:
        # Читаем файл построчно для экономии памяти
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Ищем стандартные метки уровней логирования в квадратных скобках или просто текстом
                if any(x in line.upper() for x in ['[ERROR]', ' ERROR ', 'ERROR:']):
                    stats['ERROR'] += 1
                elif any(x in line.upper() for x in ['[WARNING]', ' WARNING ', 'WARNING:', 'WARN']):
                    stats['WARNING'] += 1
                elif any(x in line.upper() for x in ['[INFO]', ' INFO ', 'INFO:']):
                    stats['INFO'] += 1
                elif any(x in line.upper() for x in ['[DEBUG]', ' DEBUG ', 'DEBUG:']):
                    stats['DEBUG'] += 1
                else:
                    stats['OTHER'] += 1
    except Exception as e:
        logger.error(f"Ошибка при анализе категорий логов: {e}")
        
    return stats


def get_log_file_info(log_file_path=None):
    """
    Собирает полную информацию о лог-файле для вывода в админке.
    Возвращает словарь с метаданными.
    """
    if log_file_path is None:
        log_file_path = get_log_file_path()
        
    if not log_file_path or not os.path.exists(log_file_path):
        return {
            'exists': False,
            'file_name': 'debug.log',
            'file_path': 'Не найден',
            'size': 0,
            'human_size': '0 KB',
            'total_lines': 0,
            'last_modified': None,
            'categories': count_lines_by_category(None)
        }
        
    # Получаем статистику файла из ОС
    stat = os.stat(log_file_path)
    size_bytes = stat.st_size
    
    # Формируем данные
    info = {
        'exists': True,
        'file_name': os.path.basename(log_file_path),
        'file_path': log_file_path,
        'size': size_bytes,
        'human_size': _format_file_size(size_bytes),
        'total_lines': count_total_lines(log_file_path),
        'last_modified': timezone.make_aware(datetime.fromtimestamp(stat.st_mtime)),
        'categories': count_lines_by_category(log_file_path)
    }
    return info


def get_error_log_file_info():
    """Специализированная функция для получения инфо о логе ошибок."""
    return get_log_file_info(get_error_log_file_path())


def get_recent_log_lines(count=50, log_file_path=None):
    """
    Извлекает последние N строк из лог-файла.
    Используется для быстрого просмотра в веб-интерфейсе.
    """
    if log_file_path is None:
        log_file_path = get_log_file_path()
        
    if not log_file_path or not os.path.exists(log_file_path):
        return []
        
    lines = []
    try:
        # Читаем файл целиком (для 50 строк это допустимо)
        # В идеале здесь можно использовать смещение от конца файла (f.seek), но для текста это сложнее из-за кодировок
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            lines = all_lines[-count:] if len(all_lines) > count else all_lines
    except Exception as e:
        logger.error(f"Ошибка при получении последних строк лога: {e}")
        
    return lines


def get_error_log_recent_lines(count=100):
    """Получает последние 100 строк из лога ошибок."""
    return get_recent_log_lines(count, get_error_log_file_path())


def clear_log_file(log_file_path=None, create_backup=True):
    """
    Очищает содержимое файла. По умолчанию создает резервную копию перед удалением.
    """
    if log_file_path is None:
        log_file_path = get_log_file_path()
        
    if not log_file_path or not os.path.exists(log_file_path):
        return False, "Файл не найден"
        
    try:
        # Делаем копию файла с отметкой времени
        if create_backup:
            _create_backup(log_file_path)
            
        # Открываем в режиме 'w' (перезапись), что эффективно очищает файл
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(f"--- Лог очищен {datetime.now()} ---\n")
            
        return True, "Файл успешно очищен"
    except Exception as e:
        return False, f"Ошибка при очистке: {str(e)}"


def clear_error_log_file():
    """Специализированная функция для очистки лога ошибок."""
    return clear_log_file(get_error_log_file_path())


def _format_file_size(size_bytes):
    """Преобразует байты в KB, MB, GB."""
    if size_bytes == 0:
        return "0 KB"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def _create_backup(log_file_path):
    """Создает копию файла в папке backups."""
    backup_dir = os.path.join(os.path.dirname(log_file_path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.basename(log_file_path)
    backup_path = os.path.join(backup_dir, f"{file_name}.{timestamp}.bak")
    
    shutil.copy2(log_file_path, backup_path)
    return backup_path