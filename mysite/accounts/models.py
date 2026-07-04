# accounts/models.py
# Модели для приложения accounts (аккаунты пользователей)

from django.db import models  # Импорт базовых моделей Django
from django.contrib.auth.models import User  # Импорт модели пользователя Django
from django.utils.translation import gettext_lazy as _  # Функция для локализации строк
from django.core.exceptions import ValidationError  # Исключение для валидации данных
from django.urls import reverse  # Генерация URL по имени маршрута
import os  # Работа с файловыми путями
import logging  # Логирование
import uuid  # Генерация уникальных токенов
from datetime import timedelta  # Вычисление времени жизни токенов
from django.utils import timezone  # Текущее время с учётом часового пояса

# Настройка логгера для данного модуля
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Функция генерирует путь для загрузки аватара пользователя.
# ---------------------------------------------------------------------------
def avatar_upload_path(instance, filename):
    """Генерирует путь для сохранения аватара.

    Args:
        instance: Экземпляр модели UserProfile.
        filename: Исходное имя загружаемого файла.

    Returns:
        str: Путь внутри директории «avatars».
    """
    ext = filename.split('.')[-1].lower()  # Получаем расширение (нижний регистр)
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']  # Разрешённые форматы
    if ext not in valid_extensions:
        raise ValueError(_("Недопустимое расширение файла"))
    # Формируем новое имя, включающее ID пользователя
    filename = f"avatar_user_{instance.user.id}.{ext}"
    return os.path.join('avatars', filename)  # Возврат полного относительного пути

# ---------------------------------------------------------------------------
# Модель профиля пользователя. Хранит дополнительную информацию.
# ---------------------------------------------------------------------------
class UserProfile(models.Model):
    """Расширенный профиль пользователя.

    Содержит данные, которые не входят в базовую модель User, такие
    как телефон, аватар и биография.
    """
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
    totp_secret = models.CharField(
        _("TOTP‑секрет"),
        max_length=32,
        blank=True,
        null=True,
        help_text=_("Секрет для двухфакторной аутентификации (TOTP)"),
    )
    bio = models.TextField(_("О себе"), blank=True, max_length=1000)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        """Метаданные модели.

        verbose_name – отображаемое имя в админке.
        ordering – порядок сортировки по умолчанию.
        """
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")
        ordering = ["-created_at"]

    def __str__(self):
        """Текстовое представление модели для админки и отладки."""
        return f"Профиль {self.user.username}"

    @property
    def get_avatar_url(self):
        """Возвращает URL аватара либо URL изображения по умолчанию."""
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "/static/accounts/images/default-avatar.png"

    @property
    def role_display(self):
        """Определяет человекочитаемую роль пользователя.

        Приоритет: superuser → staff → группы → пользователь.
        """
        if self.user.is_superuser:
            return "Администратор"
        if self.user.is_staff:
            return "Сотрудник"
        groups = self.user.groups.values_list("name", flat=True)
        if "Модераторы" in groups:
            return "Модератор"
        return "Пользователь"

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматической обработки аватара.

        После сохранения файл обрезается до квадрата 200×200 пикселей.
        """
        super().save(*args, **kwargs)  # Сначала сохраняем файл на диск
        if self.avatar:
            try:
                from PIL import Image
                img = Image.open(self.avatar.path)
                # Обрезаем центр до квадратного размера
                min_dim = min(img.size)
                left = (img.width - min_dim) // 2
                top = (img.height - min_dim) // 2
                img = img.crop((left, top, left + min_dim, top + min_dim))
                img = img.resize((200, 200), Image.LANCZOS)
                img.save(self.avatar.path, optimize=True, quality=85)
                logger.info(f"Аватар пользователя {self.user.username} обрезан до 200x200")
            except Exception as e:
                logger.warning(f"Не удалось обработать аватар {self.user.username}: {e}")

    def clean(self):
        """Валидация модели перед сохранением.

        Проверяем корректность номера телефона.
        """
        super().clean()
        if self.phone and not self.phone.startswith('+'):
            raise ValidationError({"phone": _("Номер телефона должен начинаться с '+'")})

# ---------------------------------------------------------------------------
# Модель токена подтверждения email (регистрация).
# ---------------------------------------------------------------------------
class EmailVerificationToken(models.Model):
    """Токен для подтверждения email при регистрации.

    Токен одноразовый, действует ограниченное время.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="email_verification",
        verbose_name=_("Пользователь"),
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _("Токен подтверждения email")
        verbose_name_plural = _("Токены подтверждения email")
        indexes = [models.Index(fields=["token", "expires_at"]) ]

    def save(self, *args, **kwargs):
        """При сохранении автоматически рассчитывается время истечения (24 часа)."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Проверка, не истёк ли токен."""
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"EmailToken(user={self.user.username}, valid={self.is_valid()})"

# ---------------------------------------------------------------------------
# Модель токена сброса пароля.
# ---------------------------------------------------------------------------
class PasswordResetToken(models.Model):
    """Токен для восстановления пароля.

    Одноразовый, действует ограниченное время (по умолчанию 1 час).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
        verbose_name=_("Пользователь"),
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _("Токен сброса пароля")
        verbose_name_plural = _("Токены сброса пароля")
        indexes = [models.Index(fields=["token", "expires_at"]) ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"PasswordResetToken(user={self.user.username}, valid={self.is_valid()})"

# ---------------------------------------------------------------------------
# Модель журнала активности пользователя.
# ---------------------------------------------------------------------------
class ActivityLog(models.Model):
    """Записывает действия пользователя в системе.

    Полезно для аудита и анализа поведения.
    """
    ACTION_CHOICES = [
        ("login", _("Вход в систему")),
        ("logout", _("Выход из системы")),
        ("profile_update", _("Обновление профиля")),
        ("password_change", _("Смена пароля")),
        ("2fa_setup", _("Настройка 2FA")),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        verbose_name=_("Пользователь"),
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name=_("Действие"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP адрес"))
    user_agent = models.CharField(max_length=255, blank=True, verbose_name=_("User-Agent"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Время"))

    class Meta:
        verbose_name = _("Запись активности")
        verbose_name_plural = _("Записи активности")
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["user", "action", "timestamp"]) ]

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} @ {self.timestamp}"

# ---------------------------------------------------------------------------
# Существующие модели тикетов (без изменений).
# ---------------------------------------------------------------------------
class Ticket(models.Model):
    """Модель тикета технической поддержки.

    Пользователь может создавать обращения, а сотрудники отвечать.
    """
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
        _("Статус"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
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
        return reverse("accounts:ticket_detail", kwargs={"pk": self.pk})

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    @property
    def is_closed(self):
        return self.status == self.STATUS_CLOSED

    def can_user_access(self, user):
        return user == self.user or user.is_staff

class TicketResponse(models.Model):
    """Ответы на тикеты.

    Хранят сообщения администраторов и пользователей.
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        verbose_name=_("Тикет"),
        related_name="responses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
    )
    message = models.TextField(_("Сообщение"))
    is_admin_response = models.BooleanField(_("Ответ администрации"), default=False)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)

    class Meta:
        verbose_name = _("Ответ на тикет")
        verbose_name_plural = _("Ответы на тикеты")
        ordering = ["created_at"]
        indexes = [models.Index(fields=["ticket", "created_at"]) ]

    def __str__(self):
        return f"Ответ на тикет #{self.ticket.id}"

    def save(self, *args, **kwargs):
        if self.user.is_staff:
            self.is_admin_response = True
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.message.strip():
            raise ValidationError({"message": _("Сообщение не может быть пустым")})
