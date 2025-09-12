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
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]
