"""
Конфигурация URL для проекта mysite.

Список `urlpatterns` маршрутизирует URL к представлениям (views).
Для получения дополнительной информации см.:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
# mysite/urls.py
# Главный файл конфигурации URL для проекта

from django.contrib import admin  # Импорт админ-панели Django
from django.urls import path, include  # Импорт функций для работы с URL
from django.conf import settings  # Импорт настроек Django
from django.conf.urls.static import (
    static,
)  # Импорт функции для обслуживания статических файлов

# Основные маршруты URL проекта
urlpatterns = [
    path("admin/", admin.site.urls),  # Маршрут для админ-панели
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # Маршруты для CKEditor 5
    path("captcha/", include("captcha.urls")),  # Маршруты для капчи
    path("", include("main.urls")),  # Главная страница и основные маршруты
    path("news/", include("news.urls")),  # Маршруты для новостей
    path("portfolio/", include("portfolio.urls")),  # Маршруты для портфолио
    path("services/", include("services.urls")),  # Маршруты для услуг
    path("reviews/", include("reviews.urls")),  # Маршруты для отзывов
    path("accounts/", include("accounts.urls")),  # Маршруты для аккаунтов пользователей
    path("feedback/", include("feedback.urls")),  # Маршруты для обратной связи
    # path("files/", include("files.urls")),  # Маршруты для управления файлами
]

# В режиме отладки (DEBUG) добавляем обслуживание медиа файлов
if settings.DEBUG:
    # Обслуживание медиа файлов (загружаемые пользователями файлы: изображения, документы и т.д.)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Обработчики ошибок (используются только в продакшене, в DEBUG Django использует свои)
handler404 = "main.views.custom_404_view"  # Обработчик ошибки 404 (страница не найдена)
handler500 = (
    "main.views.custom_500_view"  # Обработчик ошибки 500 (внутренняя ошибка сервера)
)
