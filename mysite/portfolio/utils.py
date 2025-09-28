# portfolio/utils.py
import os
from django.utils import timezone
from urllib.parse import urlparse
from django.conf import settings


def custom_upload_to(instance, filename):
    """
    Генерирует путь для загрузки файла в формате: domain/YYYY/MM/DD/domain_YYYYMMDD_HHMMSS_original_name
    """
    # Получаем домен из настроек
    domain = "localhost"  # значение по умолчанию

    if hasattr(settings, "ALLOWED_HOSTS") and settings.ALLOWED_HOSTS:
        # Берем первый домен из ALLOWED_HOSTS, исключая wildcard
        for host in settings.ALLOWED_HOSTS:
            if host != "*" and "." in host:
                domain = host
                break

    # Очищаем домен от недопустимых символов для имени файла
    domain_clean = domain.replace(".", "_").replace("-", "_")

    # Получаем текущую дату и время
    now = timezone.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")

    # Получаем расширение файла
    name, ext = os.path.splitext(filename)

    # Генерируем новое имя файла
    new_filename = f"{domain_clean}_{date_str}_{time_str}_{name}{ext}"

    # Формируем путь с годом и месяцем для организации файлов
    return f"{domain_clean}/{now.year}/{now.month:02d}/{new_filename}"
