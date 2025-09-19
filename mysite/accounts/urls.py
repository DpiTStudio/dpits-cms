# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    # Изменяем маршрут выхода
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/update/", views.profile_update, name="profile_update"),
    path("password/change/", views.password_change, name="password_change"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]
