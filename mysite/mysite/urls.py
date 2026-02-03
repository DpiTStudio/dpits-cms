"""
Конфигурация URL для проекта mysite.

Список `urlpatterns` маршрутизирует URL к представлениям (views).
Для получения дополнительной информации см.:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
# mysite/urls.py
# Главный файл конфигурации URL для проекта

from django.contrib import admin  # Импорт админ-панели
from django.urls import path, include  # Импорт функций для работы с URL
from django.conf import settings  # Импорт настроек Django
from django.conf.urls.static import (
    static,
)  # Импорт функции для обслуживания статических файлов
from django.views.generic import TemplateView  # Для отображения robots.txt
from django.contrib.sitemaps.views import sitemap  # View для карты сайта
from .sitemaps import (
    StaticViewSitemap,
    PageSitemap,
    NewsSitemap,
    PortfolioSitemap,
    ServiceSitemap,
)  # Импорт классов карты сайта

# Настройка заголовков админ-панели
admin.site.site_header = "DPITS CMS"
admin.site.site_title = "CMS"
admin.site.index_title = "Панель управления"

# Словарь карт сайта
sitemaps = {
    "static": StaticViewSitemap,
    "pages": PageSitemap,
    "news": NewsSitemap,
    "portfolio": PortfolioSitemap,
    "services": ServiceSitemap,
}

# Основные маршруты URL проекта
urlpatterns = [
    path("admin/", admin.site.urls),  # Маршрут для админ-панели
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # Маршруты для CKEditor 5
    path("captcha/", include("captcha.urls")),  # Маршруты для капчи
    
    # SEO маршруты
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),


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

# Обработчики ошибок (используются только в продакшене, в DEBUG используются встроенные)
handler404 = "main.views.custom_404_view"  # Обработчик ошибки 404 (страница не найдена)
handler500 = (
    "main.views.custom_500_view"  # Обработчик ошибки 500 (внутренняя ошибка сервера)
)
