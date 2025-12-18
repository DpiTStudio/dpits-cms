# accounts/urls.py
# Маршруты URL для приложения accounts (аккаунты пользователей)
from django.urls import path  # Импорт функции для создания маршрутов URL
from django.contrib.auth import views as auth_views  # Импорт стандартных представлений аутентификации Django
from . import views  # Импорт представлений (views) из текущего приложения
from .forms import CustomAuthenticationForm  # Кастомная форма с капчей

app_name = "accounts"  # Пространство имен приложения (используется для обратных ссылок)

# Список маршрутов URL для приложения аккаунтов
urlpatterns = [
    # === РЕГИСТРАЦИЯ И АУТЕНТИФИКАЦИЯ ===
    
    # Регистрация нового пользователя
    # URL: /accounts/register/
    path("register/", views.register, name="register"),
    
    # Вход в систему (использует стандартное представление Django)
    # URL: /accounts/login/
    # redirect_authenticated_user=True - перенаправляет уже авторизованных пользователей
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",  # Шаблон страницы входа
            redirect_authenticated_user=True,  # Перенаправление авторизованных пользователей
            authentication_form=CustomAuthenticationForm,  # Форма входа с капчей
        ),
        name="login",
    ),
    
    # Выход из системы (кастомное представление, только POST запросы)
    # URL: /accounts/logout/
    path("logout/", views.custom_logout, name="logout"),
    
    # Страница подтверждения выхода
    # URL: /accounts/logout/confirm/
    path("logout/confirm/", views.logout_confirmation, name="logout_confirm"),
    
    # === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===
    
    # Основная страница профиля пользователя
    # URL: /accounts/profile/
    path("profile/", views.profile_view, name="profile"),
    
    # Редактирование основных данных профиля (имя, email)
    # URL: /accounts/profile/edit/
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    
    # Расширенное редактирование профиля (аватар, телефон, биография)
    # URL: /accounts/profile/update/
    path("profile/update/", views.profile_update, name="profile_update"),
    
    # Смена пароля пользователя
    # URL: /accounts/password/change/
    path("password/change/", views.password_change, name="password_change"),
    
    # === ТИКЕТЫ ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ ===
    
    # Список тикетов пользователя
    # URL: /accounts/tickets/
    path("tickets/", views.ticket_list, name="ticket_list"),
    
    # Создание нового тикета
    # URL: /accounts/tickets/create/
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    
    # Детальная страница тикета с ответами
    # URL: /accounts/tickets/<pk>/
    # pk - первичный ключ тикета (целое число)
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
]
