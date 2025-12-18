# feedback/urls.py
# URL маршруты для приложения feedback (обратная связь)

from django.urls import path  # Импорт функции для создания URL маршрутов
from . import views  # Импорт представлений приложения

app_name = "feedback"  # Имя пространства имен для URL

urlpatterns = [
    path("", views.feedback_list, name="list"),  # Список сообщений обратной связи пользователя
    path("create/", views.feedback_create, name="create"),  # Создание нового сообщения
    path("<int:pk>/", views.feedback_detail, name="detail"),  # Детальный просмотр сообщения
]

