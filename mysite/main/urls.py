# main/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "main"

urlpatterns = [
    # Главная страница
    path("", views.IndexView.as_view(), name="index"),
    # Детальная страница
    path("page/<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
    # Статические страницы
    path("contacts/", views.ContactView.as_view(), name="contacts"),
    path("about/", views.AboutView.as_view(), name="about"),
    # Профиль пользователя
    path("profile/", views.profile_view, name="profile"),
    # Обработка ошибок
    path(
        "error/404/",
        TemplateView.as_view(template_name="main/404.html"),
        name="error_404",
    ),
    path(
        "error/500/",
        TemplateView.as_view(template_name="main/500.html"),
        name="error_500",
    ),
]
