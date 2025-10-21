# apps.py
# Конфигурация приложения main
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MainConfig(AppConfig):
    """
    Конфигурация приложения 'main'.
    Определяет метаданные и поведение приложения.
    """

    # Автоматически создаваемый первичный ключ для моделей
    default_auto_field = "django.db.models.BigAutoField"

    # Имя приложения
    name = "main"

    # Человекочитаемое имя для отображения в админке
    verbose_name = _("Основные настройки")

    def ready(self):
        """
        Вызывается когда приложение готово к работе.
        Используется для регистрации сигналов.
        """
        # Импорт здесь чтобы избежать циклических импортов
        try:
            from . import signals
        except ImportError:
            # Если сигналы не определены, игнорируем ошибку
            pass
