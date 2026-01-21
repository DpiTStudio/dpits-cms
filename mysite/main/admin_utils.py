# admin_utils.py
# ВСПОМОГАТЕЛЬНЫЕ УТИЛИТЫ ДЛЯ АДМИН-ПАНЕЛИ
# 
# Этот файл содержит функции для сбора системной информации о сервере,
# конфигурации Django и окружения, которые отображаются на дашборде.

import os            # Параметры операционной системы
import sys           # Параметры Python интерпретатора
import platform      # Информация о платформе (Windows/Linux)
import socket        # Сетевые настройки и имя хоста
import psutil        # Мониторинг ресурсов (ЦПУ, память, диск)
import django        # Доступ к версии и настройкам Django
from datetime import datetime  # Работа со временем
from django.conf import settings  # Доступ к settings.py проекта


def get_server_info():
    """
    Собирает детальный отчет о состоянии сервера и приложения.
    Возвращает словарь с распределением по категориям.
    """
    # 1. Информация о платформе
    platform_info = {
        "system": platform.system(),                # Название ОС (например, Windows)
        "release": platform.release(),              # Версия релиза
        "version": platform.version(),              # Полная версия
        "machine": platform.machine(),              # Архитектура (AMD64/x86)
        "processor": platform.processor(),          # Модель процессора
        "node": platform.node(),                    # Имя сетевого узла
    }

    # 2. Окружение Python и Django
    python_django_info = {
        "python_version": sys.version,              # Версия Python
        "django_version": django.get_version(),     # Версия Django
        "executable": sys.executable,               # Путь к интерпретатору
        "base_dir": settings.BASE_DIR,              # Корневая папка проекта
    }

    # 3. Информация о хосте и сети
    try:
        host_name = socket.gethostname()            # Имя хоста
        host_ip = socket.gethostbyname(host_name)   # IP адрес хоста
    except Exception:
        host_name = "N/A"
        host_ip = "N/A"

    host_info = {
        "host_name": host_name,
        "host_ip": host_ip,
    }

    # 4. Настройки Django окружения
    env_info = {
        "debug": settings.DEBUG,                    # Режим отладки (True/False)
        "time_zone": settings.TIME_ZONE,            # Часовой пояс проекта
        "language_code": settings.LANGUAGE_CODE,    # Язык по умолчанию
        "default_from_email": getattr(settings, "DEFAULT_FROM_EMAIL", "N/A"),
    }

    # 5. Состояние процесса и ресурсов
    process_info = {}
    try:
        process = psutil.Process(os.getpid())       # Текущий процесс Django
        with process.oneshot():
            process_info = {
                "pid": process.pid,                 # ID процесса
                "memory_info": format_bytes(process.memory_info().rss),  # Память (RSS)
                "cpu_percent": process.cpu_percent(), # Загрузка ЦПУ этим процессом
                "create_time": datetime.fromtimestamp(process.create_time()), # Время запуска
                "status": process.status(),         # Статус (running)
            }
    except Exception:
        pass

    # 6. Глобальные системные ресурсы
    system_resources = {}
    try:
        # Память
        virtual_mem = psutil.virtual_memory()
        # Диск
        disk_usage = psutil.disk_usage("/")
        
        system_resources = {
            "cpu_count": psutil.cpu_count(logical=True), # Кол-во ядер
            "total_memory": format_bytes(virtual_mem.total), # Всего ОЗУ
            "available_memory": format_bytes(virtual_mem.available), # Свободно ОЗУ
            "memory_percent": virtual_mem.percent, # % использования ОЗУ
            "disk_total": format_bytes(disk_usage.total), # Всего на диске
            "disk_used": format_bytes(disk_usage.used),   # Занято на диске
            "disk_free": format_bytes(disk_usage.free),   # Свободно на диске
            "disk_percent": disk_usage.percent,           # % использования диска
        }
    except Exception:
        pass

    # 7. База данных
    db_info = {
        "engine": settings.DATABASES["default"]["ENGINE"], # Движок БД
        "name": settings.DATABASES["default"]["NAME"],     # Имя БД
        "host": settings.DATABASES["default"].get("HOST", "localhost"),
    }

    # Собираем всё в один словарь
    return {
        "platform": platform_info,
        "python_django": python_django_info,
        "host": host_info,
        "environment": env_info,
        "process": process_info,
        "resources": system_resources,
        "database": db_info,
    }


def get_installed_apps_info():
    """Возвращает список всех установленных Django приложений."""
    from django.apps import apps
    return [
        {
            "name": app.name,
            "label": app.label,
            "verbose_name": app.verbose_name,
            "path": app.path,
        }
        for app in apps.get_app_configs()
    ]


def get_middleware_info():
    """Возвращает список всех активных Middleware (промежуточного ПО)."""
    return settings.MIDDLEWARE


def get_site_url():
    """
    Пытается определить базовый URL сайта (протокол + домен).
    Использует Site framework или настройки проекта.
    """
    protocol = "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"
    try:
        from django.contrib.sites.models import Site
        domain = Site.objects.get_current().domain
    except Exception:
        domain = "localhost"
    
    return f"{protocol}://{domain}"


def format_bytes(bytes_size):
    """
    Вспомогательная функция для перевода байтов в читаемый формат (КБ, МБ и т.д.).
    
    Параметры:
        bytes_size: число в байтах.
    """
    if bytes_size is None or bytes_size == 0:
        return "0 B"
        
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} EB"