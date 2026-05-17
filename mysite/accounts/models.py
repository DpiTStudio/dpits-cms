# accounts/models.py
# Модели для приложения accounts (аккаунты пользователей)
from django.db import models  # Импорт базовых моделей Django
from django.contrib.auth.models import User  # Импорт модели пользователя Django
from django.utils.translation import gettext_lazy as _  # Импорт функции для перевода строк
from django.core.exceptions import ValidationError  # Импорт исключения для валидации
from django.urls import reverse  # Функция для генерации URL
import os  # Модуль для работы с путями файловой системы
import logging  # Импорт модуля логирования

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)


def avatar_upload_path(instance, filename):
    """
    Генерация пути для загрузки аватара с проверкой расширения.
    
    Args:
        instance: Экземпляр модели UserProfile
        filename: Имя загружаемого файла
        
    Returns:
        str: Путь для сохранения файла аватара
        
    Raises:
        ValueError: Если расширение файла недопустимо
    """
    ext = filename.split(".")[-1].lower()  # Получаем расширение файла и приводим к нижнему регистру
    valid_extensions = ["jpg", "jpeg", "png", "gif"]  # Список допустимых расширений

    if ext not in valid_extensions:  # Проверяем, является ли расширение допустимым
        raise ValueError(_("Недопустимое расширение файла"))  # Вызываем ошибку, если расширение недопустимо

    filename = f"avatar_user_{instance.user.id}.{ext}"  # Формируем имя файла с ID пользователя
    return os.path.join("avatars", filename)  # Возвращаем полный путь к файлу в папке avatars


class UserProfile(models.Model):
    """
    Расширенный профиль пользователя.
    Содержит дополнительную информацию о пользователе, не входящую в стандартную модель User.
    """

    user = models.OneToOneField(
        User,  # Связь один-к-одному с моделью User
        on_delete=models.CASCADE,  # При удалении пользователя удаляется и профиль
        verbose_name=_("Пользователь"),  # Человекочитаемое имя поля
        related_name="profile",  # Имя для обратной связи (user.profile)
    )
    phone = models.CharField(
        _("Телефон"),  # Человекочитаемое имя поля
        max_length=20,  # Максимальная длина номера телефона
        blank=True,  # Поле может быть пустым в формах
        null=True,  # Поле может быть NULL в базе данных
        help_text=_("Формат: +7 XXX XXX-XX-XX"),  # Подсказка для пользователя
    )
    avatar = models.ImageField(
        _("Аватар"),  # Человекочитаемое имя поля
        upload_to=avatar_upload_path,  # Функция для генерации пути загрузки
        blank=True,  # Поле может быть пустым в формах
        null=True,  # Поле может быть NULL в базе данных
        help_text=_("Рекомендуемый размер: 200x200 пикселей"),  # Подсказка для пользователя
    )
    bio = models.TextField(_("О себе"), blank=True, max_length=1000)  # Биография пользователя, максимум 1000 символов
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)  # Дата и время создания (устанавливается автоматически)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)  # Дата и время последнего обновления (обновляется автоматически)

    class Meta:
        """Метаданные модели профиля пользователя."""
        verbose_name = _("Профиль пользователя")  # Единственное число для админки
        verbose_name_plural = _("Профили пользователей")  # Множественное число для админки
        ordering = ["-created_at"]  # Сортировка по дате создания (новые сверху)

    def __str__(self):
        """Строковое представление объекта для отображения в админке и консоли."""
        return f"Профиль {self.user.username}"  # Возвращаем строку с именем пользователя

    @property
    def get_avatar_url(self):
        """
        Получение URL аватара с fallback на изображение по умолчанию.
        
        Returns:
            str: URL аватара пользователя или URL изображения по умолчанию
        """
        if self.avatar and hasattr(self.avatar, "url"):  # Проверяем наличие аватара и метода url
            return self.avatar.url  # Возвращаем URL аватара
        return "/static/accounts/images/default-avatar.png"  # Возвращаем URL изображения по умолчанию

    @property
    def role_display(self):
        """
        Возвращает человекочитаемую роль пользователя на основе его прав и групп.

        Returns:
            str: Строка с названием роли пользователя
        """
        if self.user.is_superuser:
            return "Администратор"
        elif self.user.is_staff:
            return "Сотрудник"
        groups = self.user.groups.values_list("name", flat=True)
        if "Модераторы" in groups:
            return "Модератор"
        return "Пользователь"

    def save(self, *args, **kwargs):
        """
        Переопределение save() для автоматической обрезки и оптимизации аватара.
        После сохранения обрезает аватар до квадрата 200×200 пикселей с помощью Pillow.
        """
        super().save(*args, **kwargs)  # Сначала сохраняем, чтобы файл существовал на диске
        if self.avatar:
            try:
                from PIL import Image
                img = Image.open(self.avatar.path)
                # Обрезаем до квадрата по меньшей стороне
                min_dim = min(img.size)
                left = (img.width - min_dim) // 2
                top = (img.height - min_dim) // 2
                img = img.crop((left, top, left + min_dim, top + min_dim))
                img = img.resize((200, 200), Image.LANCZOS)
                img.save(self.avatar.path, optimize=True, quality=85)
                logger.info(f"Аватар пользователя {self.user.username} обрезан до 200x200")
            except Exception as e:
                logger.warning(f"Не удалось обрезать аватар пользователя {self.user.username}: {e}")

    def clean(self):
        """
        Валидация данных профиля перед сохранением.
        Проверяет формат номера телефона.
        
        Raises:
            ValidationError: Если номер телефона не начинается с '+'
        """
        super().clean()  # Вызываем метод clean родительского класса
        if self.phone and not self.phone.startswith("+"):  # Проверяем, начинается ли номер с '+'
            raise ValidationError(
                {"phone": _("Номер телефона должен начинаться с '+'")}  # Вызываем ошибку валидации
            )


class Ticket(models.Model):
    """
    Модель тикета технической поддержки.
    Используется для системы обращений пользователей к администрации.
    """

    # Константы статусов тикета
    STATUS_OPEN = "open"  # Тикет открыт (новый)
    STATUS_IN_PROGRESS = "in_progress"  # Тикет в обработке
    STATUS_CLOSED = "closed"  # Тикет закрыт (решен)

    # Выбор статусов для поля status
    STATUS_CHOICES = (
        (STATUS_OPEN, "Открыт"),  # Вариант 1: Открыт
        (STATUS_IN_PROGRESS, "В обработке"),  # Вариант 2: В обработке
        (STATUS_CLOSED, "Закрыт"),  # Вариант 3: Закрыт
    )

    user = models.ForeignKey(
        User,  # Связь многие-к-одному с моделью User (один пользователь может иметь много тикетов)
        on_delete=models.CASCADE,  # При удалении пользователя удаляются все его тикеты
        verbose_name=_("Пользователь"),  # Человекочитаемое имя поля
        related_name="tickets",  # Имя для обратной связи (user.tickets)
    )
    subject = models.CharField(_("Тема"), max_length=200)  # Тема тикета, максимум 200 символов
    message = models.TextField(_("Сообщение"))  # Текст сообщения тикета (без ограничения длины)
    status = models.CharField(
        _("Статус"),  # Человекочитаемое имя поля
        max_length=20,  # Максимальная длина статуса
        choices=STATUS_CHOICES,  # Выбор из предопределенных статусов
        default=STATUS_OPEN  # Статус по умолчанию - открыт
    )
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)  # Дата и время создания (устанавливается автоматически)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)  # Дата и время последнего обновления (обновляется автоматически)

    class Meta:
        """Метаданные модели тикета."""
        verbose_name = _("Тикет")  # Единственное число для админки
        verbose_name_plural = _("Тикеты")  # Множественное число для админки
        ordering = ["-created_at"]  # Сортировка по дате создания (новые сверху)
        indexes = [
            models.Index(fields=["status", "created_at"]),  # Индекс для быстрого поиска по статусу и дате
            models.Index(fields=["user", "created_at"]),  # Индекс для быстрого поиска по пользователю и дате
        ]

    def __str__(self):
        """Строковое представление объекта для отображения в админке и консоли."""
        return f"Тикет #{self.id} - {self.subject}"  # Возвращаем строку с ID и темой тикета

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для просмотра тикета.
        Используется в админке и шаблонах.
        
        Returns:
            str: URL страницы детального просмотра тикета
        """
        return reverse("accounts:ticket_detail", kwargs={"pk": self.pk})  # Генерируем URL используя имя маршрута и ID тикета

    @property
    def is_open(self):
        """
        Проверяет, открыт ли тикет.
        
        Returns:
            bool: True если тикет открыт, False в противном случае
        """
        return self.status == self.STATUS_OPEN  # Возвращаем True если статус равен "open"

    @property
    def is_closed(self):
        """
        Проверяет, закрыт ли тикет.
        
        Returns:
            bool: True если тикет закрыт, False в противном случае
        """
        return self.status == self.STATUS_CLOSED  # Возвращаем True если статус равен "closed"

    def can_user_access(self, user):
        """
        Проверка прав доступа к тикету.
        Пользователь может просматривать тикет, если он является его автором или является сотрудником (staff).
        
        Args:
            user: Экземпляр модели User для проверки доступа
            
        Returns:
            bool: True если пользователь имеет доступ, False в противном случае
        """
        return user == self.user or user.is_staff  # Возвращаем True если пользователь - автор или сотрудник


class TicketResponse(models.Model):
    """
    Ответы на тикеты.
    Модель для хранения сообщений в системе тикетов технической поддержки.
    """

    ticket = models.ForeignKey(
        Ticket,  # Связь многие-к-одному с моделью Ticket (один тикет может иметь много ответов)
        on_delete=models.CASCADE,  # При удалении тикета удаляются все его ответы
        verbose_name=_("Тикет"),  # Человекочитаемое имя поля
        related_name="responses",  # Имя для обратной связи (ticket.responses)
    )
    user = models.ForeignKey(
        User,  # Связь многие-к-одному с моделью User (один пользователь может оставить много ответов)
        on_delete=models.CASCADE,  # При удалении пользователя удаляются все его ответы
        verbose_name=_("Пользователь")  # Человекочитаемое имя поля
    )
    message = models.TextField(_("Сообщение"))  # Текст ответа (без ограничения длины)
    is_admin_response = models.BooleanField(_("Ответ администрации"), default=False)  # Флаг, является ли ответ от администрации
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)  # Дата и время создания (устанавливается автоматически)

    class Meta:
        """Метаданные модели ответа на тикет."""
        verbose_name = _("Ответ на тикет")  # Единственное число для админки
        verbose_name_plural = _("Ответы на тикеты")  # Множественное число для админки
        ordering = ["created_at"]  # Сортировка по дате создания (старые сверху)
        indexes = [
            models.Index(fields=["ticket", "created_at"]),  # Индекс для быстрого поиска по тикету и дате
        ]

    def __str__(self):
        """Строковое представление объекта для отображения в админке и консоли."""
        return f"Ответ на тикет #{self.ticket.id}"  # Возвращаем строку с ID тикета

    def save(self, *args, **kwargs):
        """
        Автоматическая установка флага is_admin_response при сохранении.
        Если пользователь является сотрудником (staff), ответ помечается как ответ администрации.
        """
        if self.user.is_staff:  # Проверяем, является ли пользователь сотрудником
            self.is_admin_response = True  # Устанавливаем флаг ответа администрации
        super().save(*args, **kwargs)  # Вызываем метод save родительского класса

    def clean(self):
        """
        Валидация ответа перед сохранением.
        Проверяет, что сообщение не пустое.
        
        Raises:
            ValidationError: Если сообщение пустое или содержит только пробелы
        """
        super().clean()  # Вызываем метод clean родительского класса
        if not self.message.strip():  # Проверяем, что сообщение не пустое (после удаления пробелов)
            raise ValidationError({"message": _("Сообщение не может быть пустым")})  # Вызываем ошибку валидации
