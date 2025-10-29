# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import os


def avatar_upload_path(instance, filename):
    """Генерация пути для загрузки аватара с проверкой расширения"""
    ext = filename.split(".")[-1].lower()
    valid_extensions = ["jpg", "jpeg", "png", "gif"]

    if ext not in valid_extensions:
        raise ValueError(_("Недопустимое расширение файла"))

    filename = f"avatar_user_{instance.user.id}.{ext}"
    return os.path.join("avatars", filename)


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="profile",
    )
    phone = models.CharField(
        _("Телефон"),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Формат: +7 XXX XXX-XX-XX"),
    )
    avatar = models.ImageField(
        _("Аватар"),
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        help_text=_("Рекомендуемый размер: 200x200 пикселей"),
    )
    bio = models.TextField(_("О себе"), blank=True, max_length=1000)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Профиль {self.user.username}"

    @property
    def get_avatar_url(self):
        """Получение URL аватара с fallback"""
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "/static1/accounts/images/default-avatar.png"

    def clean(self):
        """Валидация данных профиля"""
        super().clean()
        if self.phone and not self.phone.startswith("+"):
            raise ValidationError(
                {"phone": _("Номер телефона должен начинаться с '+'")}
            )


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания/обновления профиля пользователя
    с улучшенной обработкой ошибок
    """
    try:
        if created:
            UserProfile.objects.create(user=instance)
        else:
            # Используем get_or_create для избежания исключений
            profile, created = UserProfile.objects.get_or_create(user=instance)
            if not created:
                profile.save()
    except Exception as e:
        # Логирование ошибки в реальном приложении
        print(f"Ошибка создания профиля: {e}")


class Ticket(models.Model):
    """Модель тикета технической поддержки"""

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
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"Тикет #{self.id} - {self.subject}"

    def get_absolute_url(self):
        """URL для просмотра тикета"""
        return reverse("accounts:ticket_detail", kwargs={"pk": self.pk})

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    @property
    def is_closed(self):
        return self.status == self.STATUS_CLOSED

    def can_user_access(self, user):
        """Проверка прав доступа к тикету"""
        return user == self.user or user.is_staff


class TicketResponse(models.Model):
    """Ответы на тикеты"""

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
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
        ]

    def __str__(self):
        return f"Ответ на тикет #{self.ticket.id}"

    def save(self, *args, **kwargs):
        """Автоматическая установка is_admin_response"""
        if self.user.is_staff:
            self.is_admin_response = True
        super().save(*args, **kwargs)

    def clean(self):
        """Валидация ответа"""
        super().clean()
        if not self.message.strip():
            raise ValidationError({"message": _("Сообщение не может быть пустым")})
