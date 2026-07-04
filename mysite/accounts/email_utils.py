# accounts/email_utils.py
"""Утилиты для отправки электронных писем, связанных с подтверждением email и сбросом пароля.

Каждая функция принимает объект пользователя и генерирует соответствующий токен,
после чего формирует URL‑ссылку и отправляет письмо через Django `send_mail`.
"""

import logging
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .models import EmailVerificationToken, PasswordResetToken

logger = logging.getLogger(__name__)


def send_email_verification(user, request):
    """Создать токен подтверждения email и отправить письмо пользователю.

    Параметры:
        user: экземпляр `User`
        request: текущий HttpRequest (для построения полного URL)
    """
    token_obj, created = EmailVerificationToken.objects.get_or_create(user=user)
    if not created:
        token_obj.save()
    verification_url = request.build_absolute_uri(
        reverse('accounts:email_verify', kwargs={'token': str(token_obj.token)})
    )
    subject = "Подтверждение электронной почты"
    message = (
        f"Здравствуйте, {user.username}!\n\n"
        "Для завершения регистрации подтвердите ваш email, перейдя по ссылке ниже:\n"
        f"{verification_url}\n\n"
        "Если вы не регистрировались на нашем сайте, просто игнорируйте это письмо."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    logger.info("Отправлено письмо подтверждения email для %s", user.email)


def send_password_reset(user, request):
    """Создать токен сброса пароля и отправить письмо с инструкциями.

    Параметры аналогичны `send_email_verification`.
    """
    token_obj = PasswordResetToken.objects.create(user=user)
    reset_url = request.build_absolute_uri(
        reverse('accounts:password_reset_confirm', kwargs={'token': str(token_obj.token)})
    )
    subject = "Сброс пароля"
    message = (
        f"Здравствуйте, {user.username}!\n\n"
        "Для сброса пароля перейдите по ссылке ниже:\n"
        f"{reset_url}\n\n"
        "Если вы не запрашивали сброс пароля, просто игнорируйте это письмо."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    logger.info("Отправлено письмо сброса пароля для %s", user.email)
