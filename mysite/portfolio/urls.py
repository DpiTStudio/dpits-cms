# portfolio/urls.py
from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.portfolio_list, name="list"),
    path("categories/", views.portfolio_categories, name="categories"),
    path("item/<slug:slug>/", views.portfolio_detail, name="detail"),
    path("dashboard/", views.client_dashboard, name="client_dashboard"),
    path("profile/", views.client_profile, name="client_profile"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/create/", views.create_order, name="create_order"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("review/<slug:item_slug>/", views.create_review, name="create_review"),
]
