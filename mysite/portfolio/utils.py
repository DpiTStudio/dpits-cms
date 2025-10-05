# portfolio/utils.py
import os
import uuid
from django.utils.text import slugify
from django.utils import timezone


def custom_upload_to(instance, filename):
    """
    Генерирует путь для загрузки файлов с уникальным именем
    """
    # Получаем расширение файла
    ext = filename.split(".")[-1]

    # Генерируем уникальное имя файла
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    # Определяем базовую папку в зависимости от типа модели
    if hasattr(instance, "_meta"):
        model_name = instance._meta.model_name
    else:
        model_name = "unknown"

    # Создаем путь: media/{model_name}/{year}/{month}/{filename}
    year = timezone.now().strftime("%Y")
    month = timezone.now().strftime("%m")

    return os.path.join(model_name, year, month, unique_filename)


def generate_slug(instance, slug_field="slug", title_field="title"):
    """
    Генерирует уникальный slug на основе названия
    """
    if not getattr(instance, slug_field):
        base_slug = slugify(getattr(instance, title_field))
        slug = base_slug
        counter = 1

        # Проверяем уникальность slug
        model_class = instance.__class__
        while model_class.objects.filter(**{slug_field: slug}).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        setattr(instance, slug_field, slug)

    return getattr(instance, slug_field)


def get_client_ip(request):
    """
    Получает IP адрес клиента
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def format_file_size(size_bytes):
    """
    Форматирует размер файла в читаемый вид
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"
