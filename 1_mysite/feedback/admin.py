# feedback/admin.py
# Административный интерфейс для приложения feedback (обратная связь)

from django.contrib import admin  # Импорт админ-панели Django
from django.utils.html import format_html  # Импорт функции для форматирования HTML
from django.urls import reverse  # Функция для генерации URL
from django.utils.safestring import mark_safe  # Импорт функции для безопасных HTML строк
from .models import FeedbackMessage  # Импорт модели сообщения обратной связи


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления сообщениями обратной связи.
    Предоставляет удобные инструменты для просмотра, фильтрации и управления сообщениями.
    """
    
    list_display = [
        "id",  # ID сообщения
        "get_user_link",  # Ссылка на пользователя
        "subject_short",  # Краткая тема
        "email",  # Email для ответа
        "status",  # Статус (для редактирования)
        "status_badge",  # Статус с цветовой индикацией
        "email_sent_icon",  # Иконка отправки email
        "created_at",  # Дата создания
    ]
    list_filter = [
        "status",  # Фильтр по статусу
        "email_sent",  # Фильтр по отправке email
        "created_at",  # Фильтр по дате создания
    ]
    search_fields = [
        "subject",  # Поиск по теме
        "message",  # Поиск по сообщению
        "user__username",  # Поиск по имени пользователя
        "user__email",  # Поиск по email пользователя
        "email",  # Поиск по email для ответа
    ]
    readonly_fields = [
        "user",  # Пользователь (только для чтения)
        "created_at",  # Дата создания (только для чтения)
        "updated_at",  # Дата обновления (только для чтения)
        "email_sent",  # Статус отправки email (только для чтения)
    ]
    fieldsets = (
        (
            "Информация о пользователе",
            {
                "fields": ("user", "email"),  # Поля информации о пользователе
            },
        ),
        (
            "Сообщение",
            {
                "fields": ("subject", "message"),  # Поля сообщения
            },
        ),
        (
            "Управление",
            {
                "fields": ("status", "admin_notes"),  # Поля управления
            },
        ),
        (
            "Системная информация",
            {
                "fields": ("email_sent", "created_at", "updated_at"),  # Системные поля
                "classes": ("collapse",),  # Свернутая секция
            },
        ),
    )
    list_editable = ["status"]  # Редактируемые поля в списке
    date_hierarchy = "created_at"  # Иерархия по дате создания
    ordering = ["-created_at"]  # Сортировка по дате создания (новые сверху)
    
    def get_user_link(self, obj):
        """
        Создает ссылку на профиль пользователя в админке.
        
        Args:
            obj: Экземпляр модели FeedbackMessage
            
        Returns:
            str: HTML ссылка на пользователя
        """
        if obj.user:  # Если пользователь существует
            url = reverse("admin:auth_user_change", args=[obj.user.pk])  # Генерируем URL для редактирования пользователя
            return format_html('<a href="{}">{}</a>', url, obj.user.username)  # Возвращаем HTML ссылку
        return "-"  # Возвращаем прочерк, если пользователь не найден
    
    get_user_link.short_description = "Пользователь"  # Название колонки в списке
    
    def subject_short(self, obj):
        """
        Возвращает сокращенную тему сообщения (максимум 50 символов).
        
        Args:
            obj: Экземпляр модели FeedbackMessage
            
        Returns:
            str: Сокращенная тема
        """
        if len(obj.subject) > 50:  # Если тема длиннее 50 символов
            return obj.subject[:50] + "..."  # Обрезаем и добавляем многоточие
        return obj.subject  # Возвращаем полную тему
    
    subject_short.short_description = "Тема"  # Название колонки в списке
    
    def status_badge(self, obj):
        """
        Отображает статус сообщения с цветовой индикацией.
        
        Args:
            obj: Экземпляр модели FeedbackMessage
            
        Returns:
            str: HTML с цветным бейджем статуса
        """
        status_colors = {
            FeedbackMessage.STATUS_NEW: "red",  # Красный для новых сообщений
            FeedbackMessage.STATUS_READ: "orange",  # Оранжевый для прочитанных
            FeedbackMessage.STATUS_REPLIED: "green",  # Зеленый для отвеченных
            FeedbackMessage.STATUS_ARCHIVED: "gray",  # Серый для архивированных
        }
        color = status_colors.get(obj.status, "gray")  # Получаем цвет для статуса
        status_display = obj.get_status_display()  # Получаем отображаемое название статуса
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            status_display,
        )  # Возвращаем HTML с цветным бейджем
    
    status_badge.short_description = "Статус"  # Название колонки в списке
    
    def email_sent_icon(self, obj):
        """
        Отображает иконку статуса отправки email.
        
        Args:
            obj: Экземпляр модели FeedbackMessage
            
        Returns:
            str: HTML с иконкой
        """
        if obj.email_sent:  # Если email отправлен
            return format_html(
                '<span style="color: green; font-size: 16px;" title="Email отправлен">✓</span>'
            )  # Возвращаем зеленую галочку
        return format_html(
            '<span style="color: red; font-size: 16px;" title="Email не отправлен">✗</span>'
        )  # Возвращаем красный крестик
    
    email_sent_icon.short_description = "Email"  # Название колонки в списке
    
    def get_queryset(self, request):
        """
        Оптимизация запросов к базе данных.
        Использует select_related для загрузки связанных объектов.
        
        Args:
            request: HTTP-запрос
            
        Returns:
            QuerySet: Оптимизированный набор запросов
        """
        qs = super().get_queryset(request)  # Получаем базовый QuerySet
        return qs.select_related("user")  # Загружаем пользователя одним запросом
    
    actions = ["mark_as_read", "mark_as_replied", "mark_as_archived"]  # Действия для массовой обработки
    
    def mark_as_read(self, request, queryset):
        """
        Действие: пометить сообщения как прочитанные.
        
        Args:
            request: HTTP-запрос
            queryset: Набор выбранных сообщений
        """
        count = queryset.update(status=FeedbackMessage.STATUS_READ)  # Обновляем статус выбранных сообщений
        self.message_user(
            request, f"{count} сообщений помечено как прочитанные."
        )  # Показываем сообщение об успехе
    
    mark_as_read.short_description = "Пометить как прочитанные"  # Название действия
    
    def mark_as_replied(self, request, queryset):
        """
        Действие: пометить сообщения как отвеченные.
        
        Args:
            request: HTTP-запрос
            queryset: Набор выбранных сообщений
        """
        count = queryset.update(status=FeedbackMessage.STATUS_REPLIED)  # Обновляем статус выбранных сообщений
        self.message_user(
            request, f"{count} сообщений помечено как отвеченные."
        )  # Показываем сообщение об успехе
    
    mark_as_replied.short_description = "Пометить как отвеченные"  # Название действия
    
    def mark_as_archived(self, request, queryset):
        """
        Действие: архивировать сообщения.
        
        Args:
            request: HTTP-запрос
            queryset: Набор выбранных сообщений
        """
        count = queryset.update(status=FeedbackMessage.STATUS_ARCHIVED)  # Обновляем статус выбранных сообщений
        self.message_user(
            request, f"{count} сообщений архивировано."
        )  # Показываем сообщение об успехе
    
    mark_as_archived.short_description = "Архивировать"  # Название действия

