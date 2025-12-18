# feedback/tests.py
# Тесты для приложения feedback (обратная связь)

from django.test import TestCase  # Импорт базового класса для тестов
from django.contrib.auth.models import User  # Импорт модели пользователя
from .models import FeedbackMessage  # Импорт модели сообщения обратной связи

