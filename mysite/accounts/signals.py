# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания/обновления профиля пользователя
    """
    try:
        if created:
            UserProfile.objects.create(user=instance)
            logger.info(f"Создан профиль для пользователя {instance.username}")
        else:
            instance.profile.save()
            logger.info(f"Обновлен профиль пользователя {instance.username}")
    except Exception as e:
        logger.error(f"Ошибка обработки профиля пользователя {instance.username}: {e}")
