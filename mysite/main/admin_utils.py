# admin_utils.py
"""
Утилиты для получения информации о сервере и хостинге.
"""

import os  # Работа с файловой системой
import sys  # Доступ к системным параметрам
import platform  # Информация о платформе
import socket  # Сетевая информация
import psutil  # Системные ресурсы (память, CPU, диск)
import django  # Django framework
from datetime import datetime  # Работа с датами и временем
from django.conf import settings  # Настройки Django


def get_server_info():
    """
    Собирает информацию о сервере и окружении.
    
    Returns:
        dict: Словарь с информацией о сервере
    """
    info = {
        'platform': {  # Информация о платформе
            'system': platform.system(),  # Название ОС
            'release': platform.release(),  # Версия релиза ОС
            'version': platform.version(),  # Детальная версия ОС
            'machine': platform.machine(),  # Архитектура процессора
            'processor': platform.processor(),  # Название процессора
        },
        'python': {  # Информация о Python
            'version': sys.version,  # Версия Python
            'executable': sys.executable,  # Путь к интерпретатору
            'path': sys.path[:3],  # Первые 3 пути из sys.path
        },
        'django': {  # Информация о Django
            'version': django.get_version(),  # Версия Django
            'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE', 'Не указан'),  # Модуль настроек
        },
        'host': {  # Информация о хосте
            'name': socket.gethostname(),  # Имя хоста
            'fqdn': socket.getfqdn(),  # Полное доменное имя
        },
        'environment': {  # Окружение Django
            'debug': settings.DEBUG,  # Режим отладки
            'timezone': settings.TIME_ZONE,  # Часовой пояс
            'language_code': settings.LANGUAGE_CODE,  # Код языка
            'static_root': settings.STATIC_ROOT,  # Каталог статических файлов
            'media_root': settings.MEDIA_ROOT,  # Каталог медиафайлов
            'allowed_hosts': settings.ALLOWED_HOSTS,  # Разрешенные хосты
        }
    }
    
    # Информация о процессе Django
    try:
        process = psutil.Process()  # Получаем текущий процесс
        info['process'] = {
            'pid': process.pid,  # ID процесса
            'name': process.name(),  # Имя процесса
            'memory_percent': process.memory_percent(),  # Процент используемой памяти
            'cpu_percent': process.cpu_percent(interval=0.1),  # Процент использования CPU
            'create_time': datetime.fromtimestamp(process.create_time()),  # Время создания
            'status': process.status(),  # Статус процесса
        }
    except (ImportError, AttributeError, psutil.NoSuchProcess):
        info['process'] = {'error': 'Информация о процессе недоступна'}
    
    # Информация о системе
    try:
        info['system'] = {
            'cpu_count': psutil.cpu_count(),  # Количество ядер CPU
            'cpu_percent': psutil.cpu_percent(interval=0.1),  # Общая загрузка CPU
            'virtual_memory': {
                'total': psutil.virtual_memory().total,  # Общий объем памяти
                'available': psutil.virtual_memory().available,  # Доступная память
                'percent': psutil.virtual_memory().percent,  # Процент использования памяти
            },
            'disk_usage': {
                'total': psutil.disk_usage('/').total,  # Общий объем диска
                'free': psutil.disk_usage('/').free,  # Свободное место
                'percent': psutil.disk_usage('/').percent,  # Процент использования диска
            },
        }
    except (ImportError, AttributeError, PermissionError):
        info['system'] = {'error': 'Информация о системе недоступна'}
    
    # Информация о базе данных
    try:
        from django.db import connection  # Импортируем соединение с БД
        db_settings = settings.DATABASES.get('default', {})  # Настройки БД по умолчанию
        info['database'] = {
            'engine': db_settings.get('ENGINE', 'Не указан'),  # Движок БД
            'name': db_settings.get('NAME', 'Не указан'),  # Имя базы данных
            'host': db_settings.get('HOST', 'localhost'),  # Хост БД
            'port': db_settings.get('PORT', 'default'),  # Порт БД
            'user': db_settings.get('USER', 'Не указан'),  # Пользователь БД
            'vendor': connection.vendor,  # Поставщик БД (postgresql, mysql и т.д.)
        }
    except Exception as e:
        info['database'] = {'error': str(e)}  # Сохраняем ошибку
    
    return info


def get_installed_apps_info():
    """
    Возвращает информацию об установленных приложениях.
    
    Returns:
        list: Список с информацией о приложениях
    """
    apps_info = []
    for app in settings.INSTALLED_APPS:  # Перебираем установленные приложения
        try:
            app_module = __import__(app)  # Импортируем модуль приложения
            apps_info.append({
                'name': app,  # Имя приложения
                'path': app_module.__file__ if hasattr(app_module, '__file__') else 'Встроенное',  # Путь к модулю
                'version': getattr(app_module, '__version__', 'Не указана'),  # Версия приложения
            })
        except (ImportError, ModuleNotFoundError):
            apps_info.append({
                'name': app,
                'path': 'Не найден',
                'version': 'Неизвестно',
            })
    
    return apps_info


def get_middleware_info():
    """
    Возвращает информацию о middleware.
    
    Returns:
        list: Список middleware
    """
    return settings.MIDDLEWARE  # Возвращаем список middleware из настроек


def get_site_url():
    """
    Получает URL сайта из настроек.
    
    Returns:
        str: URL сайта
    """
    from django.contrib.sites.models import Site  # Импортируем модель Site
    try:
        current_site = Site.objects.get_current()  # Получаем текущий сайт
        # Формируем URL с учетом SSL
        protocol = 'https' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'http'
        return f"{protocol}://{current_site.domain}"
    except Exception:
        # Возвращаем первый разрешенный хост или localhost по умолчанию
        return settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'


def format_bytes(bytes_size):
    """
    Форматирует размер в байтах в читаемый вид.
    
    Args:
        bytes_size: Размер в байтах
        
    Returns:
        str: Отформатированный размер
    """
    if bytes_size is None:
        return "0 B"
    
    # Единицы измерения
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    for unit in units:
        if bytes_size < 1024.0:  # Если размер меньше 1024 в текущей единице
            return f"{bytes_size:.1f} {unit}"  # Форматируем с одной десятичной цифрой
        bytes_size /= 1024.0  # Переводим в следующую единицу
    
    return f"{bytes_size:.1f} PB"  # Если больше TB, показываем в PB