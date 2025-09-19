# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    phone = models.CharField(_("Телефон"), max_length=20, blank=True)
    avatar = models.ImageField(_("Аватар"), upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(_("О себе"), blank=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()
    else:
        UserProfile.objects.get_or_create(user=instance)


class Ticket(models.Model):
    STATUS_CHOICES = (
        ("open", "Открыт"),
        ("in_progress", "В обработке"),
        ("closed", "Закрыт"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )
    subject = models.CharField(_("Тема"), max_length=200)
    message = models.TextField(_("Сообщение"))
    status = models.CharField(
        _("Статус"), max_length=20, choices=STATUS_CHOICES, default="open"
    )
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Тикет")
        verbose_name_plural = _("Тикеты")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.subject}"

    def get_status_class(self):
        status_classes = {
            "open": "badge bg-warning",
            "in_progress": "badge bg-info",
            "closed": "badge bg-success",
        }
        return status_classes.get(self.status, "badge bg-secondary")


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
        return f"Ответ на {self.ticket.subject}"
