# feedback/apps.py
# Конфигурация приложения feedback (обратная связь)

from django.apps import AppConfig  # Импорт базового класса конфигурации приложения
from django.utils.translation import gettext_lazy as _  # Импорт функции для перевода строк


class FeedbackConfig(AppConfig):
    """
    Конфигурация приложения обратной связи.
    Определяет метаданные и настройки приложения.
    """
    
    default_auto_field = "django.db.models.BigAutoField"  # Тип поля первичного ключа по умолчанию
    name = "feedback"  # Имя приложения
    verbose_name = _("Обратная связь")  # Человекочитаемое имя приложения для админки

