# accounts/backends.py
# Кастомный бэкенд аутентификации: вход по email ИЛИ username
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Кастомная аутентификация по email или username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # ИСПРАВЛЕНО: логируем коллизию вместо молчаливого возврата None
            logger.warning(
                f"Найдено несколько пользователей с одинаковым логином/email: {username!r}. "
                f"Проверьте уникальность email в базе данных."
            )
            return None
