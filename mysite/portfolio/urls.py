# ============================================================================================= #
# ФАЙЛ: URLS.PY                                                                                 #
# ОПИСАНИЕ:                                                                                     #
# Конфигурация маршрутизации URL для приложения Портфолио. Определяет схему адресов страниц     #
# и связывает их с соответствующими представлениями (Views).                                    #
#                                                                                               #
# НЮАНСЫ И ФУНКЦИОНАЛ:                                                                          #
# 1. Пространство имен: app_name = "portfolio" (доступ через {% url 'portfolio:...' %}).        #
# 2. Структура маршрутов:                                                                       #
#    - Публичные: / (список), /work/<slug> (деталь), /category/<slug> (категория).              #
#    - Клиентские: /client-*, /orders/*, /create-order/ - закрытые разделы.                     #
#    - Служебные: /create-news/... - для внутренних действий (создание новости из работы).      #
# 3. Параметры: Активно используются slug (текстовые ID) для SEO-friendly URL и pk (числовые ID)#
#    для специфических объектов (заказы).                                                       #
# ============================================================================================= #
# portfolio/urls.py
from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    # Список всех работ
    path("", views.PortfolioListView.as_view(), name="list"),
    # Детальная страница работы
    path("work/<slug:slug>/", views.PortfolioDetailView.as_view(), name="detail"),
    # Список категорий
    path("categories/", views.categories_view, name="categories"),
    # Детальная страница категории (Редирект на PortfolioListView с фильтром)
    path(
        "category/<slug:category_slug>/",
        views.PortfolioListView.as_view(),
        name="category_list_alt",
    ),
    # ЧПУ для категорий (например, /portfolio/cms/) - ставим в конец, чтобы не конфликтовать

    # Профиль клиента
    path("client-profile/", views.client_profile, name="client_profile"),
    # Личный кабинет клиента
    path("client-dashboard/", views.client_dashboard, name="client_dashboard"),
    # Список заказов клиента
    path("orders/", views.order_list, name="order_list"),
    # Детальная страница заказа
    path("order/<int:pk>/", views.order_detail, name="order_detail"),
    # Создание заказа
    path("create-order/", views.create_order, name="create_order"),
    # Создание отзыва
    path("create-review/<slug:slug>/", views.create_review, name="create_review"),
    path(
        "portfolio/<slug:slug>/create-news/",
        views.create_news_from_portfolio,
        name="create_news_from_portfolio",
    ),
    # ЧПУ для категорий (например, /portfolio/web-design/)
    path("<slug:category_slug>/", views.PortfolioListView.as_view(), name="category_list"),
]
