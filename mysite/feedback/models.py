# feedback/models.py
# Модели для приложения feedback (обратная связь)

from django.db import models  # Импорт базовых моделей Django
from django.contrib.auth.models import User  # Импорт модели пользователя Django
from django.utils.translation import gettext_lazy as _  # Импорт функции для перевода строк
from django.urls import reverse  # Функция для генерации URL


class FeedbackMessage(models.Model):
    """
    Модель сообщения обратной связи.
    Хранит сообщения от зарегистрированных пользователей с отправкой на почту.
    """
    
    # Константы статусов сообщения
    STATUS_NEW = "new"  # Новое сообщение (не прочитано)
    STATUS_READ = "read"  # Прочитано
    STATUS_REPLIED = "replied"  # На сообщение ответили
    STATUS_ARCHIVED = "archived"  # Архивировано
    
    # Выбор статусов для поля status
    STATUS_CHOICES = (
        (STATUS_NEW, "Новое"),  # Вариант 1: Новое
        (STATUS_READ, "Прочитано"),  # Вариант 2: Прочитано
        (STATUS_REPLIED, "Отвечено"),  # Вариант 3: Отвечено
        (STATUS_ARCHIVED, "Архивировано"),  # Вариант 4: Архивировано
    )
    
    user = models.ForeignKey(
        User,  # Связь многие-к-одному с моделью User (один пользователь может отправить много сообщений)
        on_delete=models.CASCADE,  # При удалении пользователя удаляются все его сообщения
        verbose_name=_("Пользователь"),  # Человекочитаемое имя поля
        related_name="feedback_messages",  # Имя для обратной связи (user.feedback_messages)
    )
    subject = models.CharField(
        _("Тема"),  # Человекочитаемое имя поля
        max_length=200,  # Максимальная длина темы
        help_text=_("Краткое описание вашего вопроса или сообщения"),  # Подсказка для пользователя
    )
    message = models.TextField(
        _("Сообщение"),  # Человекочитаемое имя поля
        help_text=_("Подробно опишите ваш вопрос или предложение"),  # Подсказка для пользователя
    )
    email = models.EmailField(
        _("Email для ответа"),  # Человекочитаемое имя поля
        max_length=254,  # Максимальная длина email
        help_text=_("На этот адрес будет отправлен ответ"),  # Подсказка для пользователя
    )
    status = models.CharField(
        _("Статус"),  # Человекочитаемое имя поля
        max_length=20,  # Максимальная длина статуса
        choices=STATUS_CHOICES,  # Выбор из предопределенных статусов
        default=STATUS_NEW,  # Статус по умолчанию - новое
    )
    admin_notes = models.TextField(
        _("Заметки администратора"),  # Человекочитаемое имя поля
        blank=True,  # Поле может быть пустым в формах
        help_text=_("Внутренние заметки для администраторов"),  # Подсказка для пользователя
    )
    created_at = models.DateTimeField(
        _("Создано"),  # Человекочитаемое имя поля
        auto_now_add=True,  # Дата и время создания (устанавливается автоматически)
    )
    updated_at = models.DateTimeField(
        _("Обновлено"),  # Человекочитаемое имя поля
        auto_now=True,  # Дата и время последнего обновления (обновляется автоматически)
    )
    email_sent = models.BooleanField(
        _("Email отправлен"),  # Человекочитаемое имя поля
        default=False,  # По умолчанию email не отправлен
        help_text=_("Было ли отправлено уведомление на почту"),  # Подсказка для пользователя
    )
    
    class Meta:
        """Метаданные модели сообщения обратной связи."""
        verbose_name = _("Сообщение обратной связи")  # Единственное число для админки
        verbose_name_plural = _("Обратная связь")  # Множественное число для админки
        ordering = ["-created_at"]  # Сортировка по дате создания (новые сверху)
        indexes = [
            models.Index(fields=["status", "created_at"]),  # Индекс для быстрого поиска по статусу и дате
            models.Index(fields=["user", "created_at"]),  # Индекс для быстрого поиска по пользователю и дате
        ]
    
    def __str__(self):
        """Строковое представление объекта для отображения в админке и консоли."""
        return f"Сообщение от {self.user.username}: {self.subject}"  # Возвращаем строку с именем пользователя и темой
    
    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для просмотра сообщения.
        Используется в админке и шаблонах.
        
        Returns:
            str: URL страницы детального просмотра сообщения
        """
        return reverse("feedback:detail", kwargs={"pk": self.pk})  # Генерируем URL используя имя маршрута и ID сообщения
    
    @property
    def is_new(self):
        """
        Проверяет, является ли сообщение новым.
        
        Returns:
            bool: True если сообщение новое, False в противном случае
        """
        return self.status == self.STATUS_NEW  # Возвращаем True если статус равен "new"
    
    @property
    def is_read(self):
        """
        Проверяет, прочитано ли сообщение.
        
        Returns:
            bool: True если сообщение прочитано, False в противном случае
        """
        return self.status == self.STATUS_READ  # Возвращаем True если статус равен "read"
    
    def can_user_access(self, user):
        """
        Проверка прав доступа к сообщению.
        Пользователь может просматривать сообщение, если он является его автором или является сотрудником (staff).
        
        Args:
            user: Экземпляр модели User для проверки доступа
            
        Returns:
            bool: True если пользователь имеет доступ, False в противном случае
        """
        return user == self.user or user.is_staff  # Возвращаем True если пользователь - автор или сотрудник

