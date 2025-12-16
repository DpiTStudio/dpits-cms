# feedback/views.py
# Представления (контроллеры) для приложения feedback (обратная связь)

from django.shortcuts import render, redirect, get_object_or_404  # Импорт функций для рендеринга шаблонов и перенаправления
from django.contrib import messages  # Импорт системы сообщений Django
from django.contrib.auth.decorators import login_required  # Декоратор для ограничения доступа только для зарегистрированных пользователей
from django.core.paginator import Paginator  # Импорт класса для пагинации (разбиения на страницы)
from django.db import transaction  # Импорт транзакций для безопасного сохранения данных
from django.core.mail import send_mail  # Импорт функции для отправки email
from django.conf import settings  # Импорт настроек Django
from django.template.loader import render_to_string  # Импорт функции для рендеринга шаблонов в строку
from .models import FeedbackMessage  # Импорт модели сообщения обратной связи
from .forms import FeedbackForm  # Импорт формы для создания сообщения
import logging  # Импорт модуля логирования

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)


@login_required  # Декоратор: доступ только для зарегистрированных пользователей
def feedback_create(request):
    """
    Представление для создания нового сообщения обратной связи.
    Доступно только для зарегистрированных пользователей.
    Отправляет email администратору при успешном создании сообщения.
    
    Args:
        request: HTTP-запрос от пользователя
        
    Returns:
        HttpResponse: Отрендеренный шаблон формы или редирект на список сообщений
    """
    if request.method == "POST":  # Если запрос методом POST (отправка формы)
        form = FeedbackForm(request.POST, user=request.user)  # Создаем форму с данными из POST-запроса и пользователем
        if form.is_valid():  # Если форма валидна
            try:
                # Используем транзакцию для безопасного сохранения
                with transaction.atomic():  # Начинаем транзакцию
                    feedback = form.save(commit=False)  # Создаем объект сообщения без сохранения
                    feedback.user = request.user  # Устанавливаем автора сообщения
                    feedback.save()  # Сохраняем сообщение в базе данных
                    
                    # Отправляем email администратору
                    try:
                        send_feedback_email(feedback)  # Вызываем функцию отправки email
                        feedback.email_sent = True  # Помечаем, что email отправлен
                        feedback.save(update_fields=["email_sent"])  # Сохраняем только поле email_sent
                    except Exception as e:  # Если произошла ошибка при отправке email
                        logger.error(f"Ошибка отправки email для сообщения {feedback.id}: {e}")  # Записываем ошибку в лог
                        messages.warning(
                            request, "Сообщение сохранено, но произошла ошибка при отправке email."
                        )  # Показываем предупреждение
                
                messages.success(
                    request, "Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время."
                )  # Показываем сообщение об успехе
                return redirect("feedback:list")  # Перенаправляем на список сообщений пользователя
            except Exception as e:  # Если произошла ошибка при сохранении
                logger.error(f"Ошибка сохранения сообщения обратной связи: {e}")  # Записываем ошибку в лог
                messages.error(
                    request, "Произошла ошибка при сохранении сообщения. Попробуйте позже."
                )  # Показываем общее сообщение об ошибке
        else:  # Если форма не валидна
            messages.error(
                request, "Пожалуйста, исправьте ошибки в форме."
            )  # Показываем сообщение об ошибках валидации
    else:  # Если запрос методом GET (отображение формы)
        form = FeedbackForm(user=request.user)  # Создаем пустую форму с пользователем
    
    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "feedback/create.html",  # Путь к шаблону
        {"form": form},  # Форма для создания сообщения
    )  # Рендерим шаблон с формой создания сообщения


@login_required  # Декоратор: доступ только для зарегистрированных пользователей
def feedback_list(request):
    """
    Представление для отображения списка сообщений обратной связи пользователя.
    Показывает только сообщения текущего пользователя.
    
    Args:
        request: HTTP-запрос от пользователя
        
    Returns:
        HttpResponse: Отрендеренный шаблон со списком сообщений
    """
    try:
        # Получаем сообщения только текущего пользователя
        messages_queryset = (
            FeedbackMessage.objects.filter(user=request.user)  # Фильтруем по текущему пользователю
            .order_by("-created_at")  # Сортируем по дате создания (новые сверху)
        )
        
        # Разбиваем на страницы по 10 сообщений
        paginator = Paginator(messages_queryset, 10)  # Создаем пагинатор с 10 сообщениями на страницу
        page_number = request.GET.get("page", 1)  # Получаем номер страницы из GET-параметра, по умолчанию 1
        page_obj = paginator.get_page(page_number)  # Получаем объект страницы с сообщениями
        
        feedback_messages = page_obj  # Используем объект страницы вместо списка
    except Exception as e:  # Если произошла ошибка
        feedback_messages = []  # Устанавливаем пустой список сообщений
        logger.error(f"Ошибка загрузки сообщений обратной связи: {e}")  # Записываем ошибку в лог
        messages.error(request, f"Ошибка загрузки сообщений: {str(e)}")  # Показываем сообщение об ошибке
    
    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "feedback/list.html",  # Путь к шаблону
        {"feedback_messages": feedback_messages},  # Объект страницы с сообщениями
    )  # Рендерим шаблон со списком сообщений


@login_required  # Декоратор: доступ только для зарегистрированных пользователей
def feedback_detail(request, pk):
    """
    Представление для детального просмотра сообщения обратной связи.
    Пользователь может просматривать только свои сообщения.
    
    Args:
        request: HTTP-запрос от пользователя
        pk: Первичный ключ сообщения
        
    Returns:
        HttpResponse: Отрендеренный шаблон с деталями сообщения
    """
    feedback = get_object_or_404(FeedbackMessage, pk=pk)  # Получаем сообщение по ID или возвращаем 404
    
    # Проверяем права доступа
    if not feedback.can_user_access(request.user):  # Если пользователь не имеет доступа
        messages.error(request, "У вас нет доступа к этому сообщению.")  # Показываем сообщение об ошибке
        return redirect("feedback:list")  # Перенаправляем на список сообщений
    
    # Если сообщение новое и пользователь его просматривает, помечаем как прочитанное
    if feedback.is_new and request.user == feedback.user:  # Если сообщение новое и пользователь - автор
        feedback.status = FeedbackMessage.STATUS_READ  # Меняем статус на "прочитано"
        feedback.save(update_fields=["status"])  # Сохраняем только поле status
    
    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "feedback/detail.html",  # Путь к шаблону
        {"feedback": feedback},  # Объект сообщения
    )  # Рендерим шаблон с деталями сообщения


def send_feedback_email(feedback):
    """
    Отправляет email администратору при получении нового сообщения обратной связи.
    
    Args:
        feedback: Экземпляр модели FeedbackMessage
        
    Raises:
        Exception: Если произошла ошибка при отправке email
    """
    # Получаем email администратора из настроек сайта или используем значение по умолчанию
    admin_email = getattr(settings, "ADMIN_EMAIL", None)  # Получаем email администратора из настроек
    
    # Если email администратора не настроен, пытаемся получить из SiteSettings
    if not admin_email:  # Если email администратора не найден
        try:
            from main.models import SiteSettings  # Импортируем модель настроек сайта
            
            site_settings = SiteSettings.load()  # Загружаем настройки сайта
            if site_settings.email:  # Если email указан в настройках сайта
                admin_email = site_settings.email  # Используем email из настроек сайта
        except Exception as e:  # Если произошла ошибка
            logger.warning(f"Не удалось получить email администратора из настроек: {e}")  # Записываем предупреждение в лог
    
    # Если email администратора все еще не найден, используем email первого суперпользователя
    if not admin_email:  # Если email администратора не найден
        try:
            from django.contrib.auth.models import User  # Импортируем модель пользователя
            
            admin_user = User.objects.filter(is_superuser=True).first()  # Получаем первого суперпользователя
            if admin_user and admin_user.email:  # Если суперпользователь существует и у него есть email
                admin_email = admin_user.email  # Используем email суперпользователя
        except Exception as e:  # Если произошла ошибка
            logger.warning(f"Не удалось получить email суперпользователя: {e}")  # Записываем предупреждение в лог
    
    # Если email администратора не найден, не отправляем email
    if not admin_email:  # Если email администратора не найден
        logger.error("Email администратора не настроен. Сообщение обратной связи не отправлено.")  # Записываем ошибку в лог
        return  # Выходим из функции
    
    # Формируем тему письма
    subject = f"Новое сообщение обратной связи: {feedback.subject}"  # Тема письма
    
    # Формируем текст письма
    message_text = f"""
Получено новое сообщение обратной связи от пользователя {feedback.user.username}.

Тема: {feedback.subject}
Email для ответа: {feedback.email}
Дата: {feedback.created_at.strftime('%d.%m.%Y %H:%M')}

Сообщение:
{feedback.message}

---
Это автоматическое уведомление от системы обратной связи.
    """.strip()  # Текст письма
    
    # Получаем email отправителя из настроек
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")  # Email отправителя
    
    # Отправляем email
    try:
        send_mail(
            subject,  # Тема письма
            message_text,  # Текст письма
            from_email,  # Email отправителя
            [admin_email],  # Список получателей (только администратор)
            fail_silently=False,  # Не игнорировать ошибки
        )  # Отправляем email
        logger.info(f"Email успешно отправлен администратору для сообщения {feedback.id}")  # Записываем успех в лог
    except Exception as e:  # Если произошла ошибка при отправке
        logger.error(f"Ошибка отправки email для сообщения {feedback.id}: {e}")  # Записываем ошибку в лог
        raise  # Пробрасываем исключение дальше

