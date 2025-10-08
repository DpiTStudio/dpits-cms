# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

app_name = "accounts"

urlpatterns = [
    # Регистрация и аутентификация
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
            next_page="accounts:profile",
        ),
        name="login",
    ),
    path(
        "logout/",
        views.custom_logout,
        name="logout",
    ),
    path("logout/confirm/", views.logout_confirmation, name="logout_confirm"),
    # Профиль пользователя
    path(
        "profile/",
        RedirectView.as_view(pattern_name="accounts:profile", permanent=False),
    ),
    path(
        "profile/edit/", views.profile_edit, name="profile_edit"
    ),  # ДОБАВЛЕНО: недостающий маршрут
    path("profile/update/", views.profile_update, name="profile_update"),
    path("password/change/", views.password_change, name="password_change"),
    # Тикеты
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]
