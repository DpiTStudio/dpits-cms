# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

# from django.urls import reverse
import os


def avatar_upload_path(instance, filename):
    """Генерация пути для загрузки аватара"""
    ext = filename.split(".")[-1]
    filename = f"avatar_user_{instance.user.id}.{ext}"
    return os.path.join("avatars", filename)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="profile",  # Изменено для совместимости
    )
    phone = models.CharField(_("Телефон"), max_length=20, blank=True, null=True)
    avatar = models.ImageField(
        _("Аватар"),
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
    )
    bio = models.TextField(_("О себе"), blank=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")

    def __str__(self):
        return f"Профиль {self.user.username}"

    @property
    def get_avatar_url(self):
        """Получение URL аватара с fallback"""
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "/static/accounts/images/default-avatar.png"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания/обновления профиля пользователя
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Используем try/except для обработки случая, когда профиля еще нет
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)


class Ticket(models.Model):
    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = (
        (STATUS_OPEN, "Открыт"),
        (STATUS_IN_PROGRESS, "В обработке"),
        (STATUS_CLOSED, "Закрыт"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="tickets",
    )
    subject = models.CharField(_("Тема"), max_length=200)
    message = models.TextField(_("Сообщение"))
    status = models.CharField(
        _("Статус"), max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN
    )
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Тикет")
        verbose_name_plural = _("Тикеты")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Тикет #{self.id} - {self.subject}"

    def get_absolute_url(self):
        return reverse("accounts:ticket_detail", kwargs={"pk": self.pk})

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    @property
    def is_closed(self):
        return self.status == self.STATUS_CLOSED


class TicketResponse(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        verbose_name=_("Тикет"),
        related_name="responses",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    message = models.TextField(_("Сообщение"))
    is_admin_response = models.BooleanField(_("Ответ администрации"), default=False)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)

    class Meta:
        verbose_name = _("Ответ на тикет")
        verbose_name_plural = _("Ответы на тикеты")
        ordering = ["created_at"]

    def __str__(self):
        return f"Ответ на тикет #{self.ticket.id}"

    def save(self, *args, **kwargs):
        """Автоматическая установка is_admin_response"""
        if self.user.is_staff:
            self.is_admin_response = True
        super().save(*args, **kwargs)
