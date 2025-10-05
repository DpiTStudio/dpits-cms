# portfolio/urls.py
from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    # Основные страницы портфолио
    path("", views.portfolio_list, name="list"),
    path("categories/", views.portfolio_categories, name="categories"),
    path("<slug:slug>/", views.portfolio_detail, name="detail"),
    # Отзывы
    path("<slug:slug>/review/", views.create_review, name="create_review"),
    # Заказы
    path("orders/create/", views.create_order, name="create_order"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    # Профиль клиента
    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("client/profile/", views.client_profile, name="client_profile"),
    # API endpoints
    path("api/items/", views.api_portfolio_items, name="api_items"),
]
