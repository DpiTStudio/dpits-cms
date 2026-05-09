# news/urls.py
# Маршруты URL для приложения news (новости)
from django.urls import path  # Импорт функции для создания маршрутов URL
from . import views  # Импорт представлений (views) из текущего приложения
from .feeds import LatestNewsFeed, NewsByCategoryFeed  # Импорт RSS-лент

app_name = "news"  # Пространство имен приложения (используется для обратных ссылок)

# Список маршрутов URL для приложения новостей
urlpatterns = [
    # Главная страница новостей - список всех активных новостей
    # URL: /news/
    path("", views.news_list, name="list"),
    # Страница категории новостей - список новостей определенной категории
    # URL: /news/category/<slug>/
    # slug - URL-дружественный идентификатор категории
    path("category/<slug:slug>/", views.news_by_category, name="category"),
    # Детальная страница новости - просмотр отдельной новости
    # URL: /news/<slug>/
    # slug - URL-дружественный идентификатор новости
    path("<slug:slug>/", views.news_detail, name="detail"),
    # Поиск новостей
    # URL: /news/search/
    path("search/", views.news_search, name="search"),
    # Новости по тегу
    # URL: /news/tag/<slug>/
    path("tag/<slug:slug>/", views.news_by_tag, name="by_tag"),
    # API для получения изображения категории
    path(
        "api/category-image/<int:category_id>/",
        views.get_category_image,
        name="get_category_image",
    ),
    # RSS Фиды
    path("feed/", LatestNewsFeed(), name="feed"),
    path("category/<slug:slug>/feed/", NewsByCategoryFeed(), name="category_feed"),
]
