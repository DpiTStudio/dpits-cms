# ============================================================================================= #
# ФАЙЛ: URLS.PY (MYSITE)                                                                        #
# ОПИСАНИЕ:                                                                                     #
# Корневой маршрутизатор URL всего проекта. Является точкой входа для всех HTTP-запросов.       #
# Распределяет запросы между приложениями в зависимости от URL-адреса.                          #
#                                                                                               #
# НЮАНСЫ И ФУНКЦИОНАЛ:                                                                          #
# 1. Подключение приложений (include):                                                          #
#    - Делегирует обработку подпутей соответствующим приложениям (news/, portfolio/, etc).      #
#    - Подключает 'main.urls' к корню сайта ("").                                               #
#    - Подключает системные маршруты: admin/, captcha/, ckeditor5/.                             #
# 2. Обслуживание статики и медиа:                                                              #
#    - В режиме DEBUG автоматически настраивает раздачу медиа-файлов и статики.                 #
# 3. Кастомизация админки:                                                                      #
#    - Переопределяет заголовки админ-панели (site_header, index_title).                        #
# 4. Обработчики ошибок:                                                                        #
#    - Настроены кастомные views для ошибок 404 (handler404) и 500 (handler500).                #
# ============================================================================================= #
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
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView, RedirectView
from mysite.sitemaps import sitemaps
from news.feeds import LatestNewsFeed, NewsByCategoryFeed

# Настройка заголовков админ-панели
admin.site.site_header = "DPITS CMS"
admin.site.site_title = "CMS"
admin.site.index_title = "Панель управления"

# Основные маршруты URL проекта
urlpatterns = [
    path("", include("main.urls")),  # Главная и основные маршруты
    path("admin/", admin.site.urls),  # Админ-панель
    path("ckeditor5/", include("django_ckeditor_5.urls")),  # CKEditor 5
    path("captcha/", include("captcha.urls")),  # Капча
    path("news/", include("news.urls")),  # Новости
    path("portfolio/", include("portfolio.urls")),  # Портфолио
    path("services/", include("services.urls")),  # Услуги
    path("reviews/", include("reviews.urls")),  # Отзывы
    path("accounts/", include("accounts.urls")),  # Аккаунты пользователей
    path("feedback/", include("feedback.urls")),  # Обратная связь
    path("knowledge-base/", include("knowledge_base.urls")),  # База знаний
    # path("files/", include("files.urls")),  # Управление файлами
    # === SEO и индексация ===
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    # === RSS ленты новостей ===
    path("news/feed/", LatestNewsFeed(), name="news_feed"),
    path("news/feed/<slug:slug>/", NewsByCategoryFeed(), name="news_feed_category"),
    # === Favicon ===
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL}images/favicon.ico", permanent=True
        ),
    ),
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
