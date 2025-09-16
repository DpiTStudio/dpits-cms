# reviews/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class Review(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидает модерации"),
        ("approved", "Одобрен"),
        ("rejected", "Отклонен"),
    )

    full_name = models.CharField(_("ФИО"), max_length=100)
    phone = models.CharField(_("Телефон"), max_length=20)
    email = models.EmailField(_("Email"))
    message = CKEditor5Field(_("Сообщение"), blank=True, config_name="extends")
    status = models.CharField(
        _("Статус"), max_length=10, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.created_at}"
