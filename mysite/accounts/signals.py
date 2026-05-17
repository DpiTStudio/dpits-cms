# accounts/signals.py
# Сигналы для автоматического управления профилями пользователей.
# ВАЖНО: сигнал определён ТОЛЬКО здесь, чтобы избежать двойного срабатывания.
# В models.py дублирующий @receiver был удалён.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания/обновления профиля пользователя.
    Использует get_or_create на пути обновления, чтобы безопасно обработать
    случай, когда профиль по какой-то причине отсутствует (RelatedObjectDoesNotExist).
    """
    try:
        if created:
            UserProfile.objects.create(user=instance)
            logger.info(f"Создан профиль для пользователя {instance.username}")
        else:
            # get_or_create вместо instance.profile.save() — защита от
            # RelatedObjectDoesNotExist, если профиль отсутствует
            profile, was_created = UserProfile.objects.get_or_create(user=instance)
            if not was_created:
                profile.save()
            logger.info(f"Обновлён профиль пользователя {instance.username}")
    except Exception as e:
        logger.error(f"Ошибка обработки профиля пользователя {instance.username}: {e}")
