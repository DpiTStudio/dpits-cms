# portfolio/urls.py
from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    # Список всех работ
    path("", views.PortfolioListView.as_view(), name="list"),
    # Детальная страница работы
    path("work/<slug:slug>/", views.PortfolioDetailView.as_view(), name="detail"),
    # Детальная страница категории
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    # Список категорий
    path("categories/", views.categories_view, name="categories"),
    # Профиль клиента
    path("client-profile/", views.client_profile, name="client_profile"),
    # Личный кабинет клиента
    path("client-dashboard/", views.client_dashboard, name="client_dashboard"),
    # Детальная страница заказа
    path("order/<int:pk>/", views.order_detail, name="order_detail"),
    # Создание заказа
    path("create-order/", views.create_order, name="create_order"),
    # Создание отзыва
    path("create-review/<slug:slug>/", views.create_review, name="create_review"),
]
