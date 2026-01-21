# admin_utils.py
"""
Утилиты для получения информации о сервере и хостинге.
"""

import os
import sys
import platform
import socket
import psutil
import django
from datetime import datetime
from django.conf import settings


def get_server_info():
    """
    Собирает информацию о сервере и окружении.
    
    Returns:
        dict: Словарь с информацией о сервере
    """
    info = {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'path': sys.path[:3],  # Первые 3 пути
        },
        'django': {
            'version': django.get_version(),
            'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE', 'Не указан'),
        },
        'host': {
            'name': socket.gethostname(),
            'fqdn': socket.getfqdn(),
        },
        'environment': {
            'debug': settings.DEBUG,
            'timezone': settings.TIME_ZONE,
            'language_code': settings.LANGUAGE_CODE,
            'static_root': settings.STATIC_ROOT,
            'media_root': settings.MEDIA_ROOT,
            'allowed_hosts': settings.ALLOWED_HOSTS,
        }
    }
    
    # Информация о процессе
    try:
        process = psutil.Process()
        info['process'] = {
            'pid': process.pid,
            'name': process.name(),
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(interval=0.1),
            'create_time': datetime.fromtimestamp(process.create_time()),
            'status': process.status(),
        }
    except (ImportError, AttributeError):
        info['process'] = {'error': 'psutil не установлен или недоступен'}
    
    # Информация о системе
    try:
        info['system'] = {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'virtual_memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
            },
            'disk_usage': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent,
            },
        }
    except (ImportError, AttributeError):
        info['system'] = {'error': 'psutil не установлен или недоступен'}
    
    # Информация о базе данных
    try:
        from django.db import connection
        db_settings = settings.DATABASES.get('default', {})
        info['database'] = {
            'engine': db_settings.get('ENGINE', 'Не указан'),
            'name': db_settings.get('NAME', 'Не указан'),
            'host': db_settings.get('HOST', 'localhost'),
            'port': db_settings.get('PORT', 'default'),
            'user': db_settings.get('USER', 'Не указан'),
            'vendor': connection.vendor,
        }
    except Exception as e:
        info['database'] = {'error': str(e)}
    
    return info


def get_installed_apps_info():
    """
    Возвращает информацию об установленных приложениях.
    
    Returns:
        list: Список с информацией о приложениях
    """
    apps_info = []
    for app in settings.INSTALLED_APPS:
        try:
            app_module = __import__(app)
            apps_info.append({
                'name': app,
                'path': app_module.__file__ if hasattr(app_module, '__file__') else 'Встроенное',
                'version': getattr(app_module, '__version__', 'Не указана'),
            })
        except ImportError:
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
    return settings.MIDDLEWARE


def get_site_url():
    """
    Получает URL сайта из настроек.
    
    Returns:
        str: URL сайта
    """
    from django.contrib.sites.models import Site
    try:
        current_site = Site.objects.get_current()
        return f"http{'s' if settings.SECURE_SSL_REDIRECT else ''}://{current_site.domain}"
    except:
        return settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'


def format_bytes(bytes_size):
    """
    Форматирует размер в байтах в читаемый вид.
    
    Args:
        bytes_size: Размер в байтах
        
    Returns:
        str: Отформатированный размер
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"