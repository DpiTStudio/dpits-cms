# portfolio/urls.py

from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.portfolio_list, name="list"),
    path("category/<slug:slug>/", views.portfolio_by_category, name="category"),
    path("<slug:slug>/", views.portfolio_detail, name="detail"),
]
