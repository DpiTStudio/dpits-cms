# services/apps.py
# Назначение: Конфигурация приложения Django. Определяет настройки приложения "services".

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    """
    Конфигурация приложения для управления услугами.
    """
    default_auto_field = "django.db.models.BigAutoField"  # Тип поля автоинкремента по умолчанию
    name = "services"                                      # Внутреннее имя приложения
    verbose_name = "Услуги"                                # Отображаемое имя в админке

    def ready(self):
        """
        Метод вызывается при запуске Django.
        Импортируем сигналы, чтобы они зарегистрировались.
        """
        import services.signals  # Регистрируем сигналы (например, создание новостей при добавлении услуги)