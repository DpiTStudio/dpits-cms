# urls.py (дополненный)
"""
МАРШРУТЫ URL ДЛЯ ПРИЛОЖЕНИЯ MAIN

Этот файл определяет все URL-маршруты для публичной части приложения main.
Каждый маршрут связывает URL-адрес с соответствующим представлением (view).

Структура URL:
- Главная страница и основные разделы
- Динамические страницы контента
- Статические страницы
- Страница профиля пользователя
- Страницы ошибок
- Статистика логов

Все маршруты находятся в пространстве имен 'main' для избежания конфликтов.
"""

from django.urls import path  # Функция для создания URL-маршрутов
from django.views.generic import (
    TemplateView,
)  # Класс для простых шаблонных представлений
from . import views  # Импорт всех представлений из текущего пакета

app_name = "main"  # Пространство имен приложения
# Позволяет использовать reverse('main:имя_маршрута')

urlpatterns = [
    # Главная страница
    path("", views.IndexView.as_view(), name="index"),
    # Пустая строка = корневой URL сайта
    # Связывается с IndexView (главная страница)
    # Детальная страница
    path("page/<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
    # Маршрут с параметром slug (человекочитаемый идентификатор)
    # Пример: /page/o-nas/
    # Статические страницы
    path("contacts/", views.ContactView.as_view(), name="contacts"),
    # Страница контактов
    path("about/", views.AboutView.as_view(), name="about"),
    # Страница "О нас"
    path("api/search/", views.SearchApiView.as_view(), name="search_api"),
    path("search/", views.SearchView.as_view(), name="search"),
    # Страница поиска
    # Страница профиля пользователя
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # Личный кабинет пользователя
    # Обработка ошибок
    path(
        "error/404/",
        TemplateView.as_view(template_name="main/404.html"),
        name="error_404",
    ),
    # Тестовая страница 404 ошибки
    path(
        "error/500/",
        TemplateView.as_view(template_name="main/500.html"),
        name="error_500",
    ),
    # Тестовая страница 500 ошибки
    # Статистика логов
    path("log-stats/", views.LogStatsView.as_view(), name="log_stats"),
    # Страница статистики логов (только для администраторов)
    # Лог ошибок
    path("error-log/", views.ErrorLogView.as_view(), name="error_log"),
    # Страница просмотра error.log (только для суперпользователей)
]
