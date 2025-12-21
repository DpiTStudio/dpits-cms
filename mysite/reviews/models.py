# reviews/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Review(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидает модерации"),
        ("approved", "Одобрен"),
        ("rejected", "Отклонен"),
    )

    author = models.ForeignKey(
        User,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,  # если автор может быть не указан
        blank=True,  # если поле может быть пустым в формах
    )
    email = models.EmailField(_("Email"), max_length=254)
    full_name = models.CharField(_("ФИО"), max_length=100)
    message = models.TextField(_("Сообщение"))
    phone = models.CharField(_("Телефон"), max_length=20)
    status = models.CharField(
        _("Статус"), max_length=10, choices=STATUS_CHOICES, default="pending"
    )
    id_review = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.created_at}"
