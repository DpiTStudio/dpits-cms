# portfolio/apps.py
# ------ -------
from django.apps import AppConfig  # Импортируем класс AppConfig


class PortfolioConfig(
    AppConfig
):  # Создаем новый класс PortfolioConfig, наследующий от AppConfig
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolio"

    def ready(self):  # Метод ready() вызывается при запуске приложения
        # Импортируем сигналы
        import portfolio.signals
