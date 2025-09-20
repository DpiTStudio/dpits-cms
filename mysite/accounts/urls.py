# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Регистрация и аутентификация
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            template_name="accounts/logout.html", next_page="/"
        ),
        name="logout",
    ),
    path("logout/confirm/", views.logout_confirmation, name="logout_confirm"),
    # Профиль пользователя
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/update/", views.profile_update, name="profile_update"),
    path("password/change/", views.password_change, name="password_change"),
    # Тикеты
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]

handler400 = "main.views.handler400"
handler403 = "main.views.handler403"
handler404 = "main.views.handler404"
handler500 = "main.views.handler500"
