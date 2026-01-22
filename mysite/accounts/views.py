# accounts/views.py
# Представления (контроллеры) для управления аккаунтами и системой тикетов

from django.shortcuts import render, redirect, get_object_or_404, reverse
from main.breadcrumbs import get_breadcrumbs
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
import logging

# Импорт моделей и форм
from .models import Ticket, UserProfile
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    TicketForm,
    TicketResponseForm,
    CustomPasswordChangeForm,
    ProfileEditForm,
)

# Настройка логгера для записи ошибок в файл или консоль
logger = logging.getLogger(__name__)


def register(request):
    """
    Регистрация нового пользователя.
    Если пользователь уже вошел, перенаправляет в профиль.
    При успешной регистрации создает пользователя, авторизует его и перенаправляет в профиль.
    """
    if request.user.is_authenticated:
        messages.info(request, "Вы уже авторизованы!")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        try:
            if form.is_valid():
                with (
                    transaction.atomic()
                ):  # Атомарная транзакция для безопасности данных
                    user = form.save()
                    login(request, user)  # Автоматический вход после регистрации
                    messages.success(
                        request, "✅ Регистрация прошла успешно! Добро пожаловать!"
                    )
                    return redirect("accounts:profile")
            else:
                messages.error(request, "❌ Пожалуйста, исправьте ошибки в форме.")
        except Exception as e:
            logger.error(f"Ошибка регистрации: {e}")
            messages.error(
                request, "❌ Произошла ошибка при регистрации. Попробуйте позже."
            )
    else:
        form = UserRegisterForm()

    context = {
        "form": form,
        "breadcrumbs": get_breadcrumbs([
            ("Регистрация", None, "fas fa-user-plus"),
        ])
    }
    return render(request, "accounts/register.html", context)


def get_reviews_count(user):
    """
    Вспомогательная функция для получения количества отзывов пользователя.
    Использует ленивый импорт для избежания циклических зависимостей.
    """
    try:
        from reviews.models import Review

        return Review.objects.filter(author=user).count()
    except (ImportError, Exception):
        return 0


def get_comments_count(user):
    """
    Вспомогательная функция для получения количества комментариев пользователя.
    Использует ленивый импорт из гипотетического приложения комментариев.
    """
    try:
        # Предполагаем наличие приложения comments
        from comments.models import Comment

        return Comment.objects.filter(author=user).count()
    except (ImportError, Exception):
        return 0


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """
    Редактирование основных данных (User model): username, email, имя, фамилия.
    """
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Профиль успешно обновлен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "❌ Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ProfileEditForm(instance=request.user)

    context = {
        "form": form,
        "breadcrumbs": get_breadcrumbs([
            ("Личный кабинет", reverse("accounts:profile"), "fas fa-user"),
            ("Редактирование данных", None, "fas fa-user-edit"),
        ])
    }
    return render(request, "accounts/profile_edit.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_update(request):
    """
    Обновление расширенных данных профиля (UserProfile model): телефон, аватар, био.
    Использует две формы в одном представлении.
    """
    try:
        # Получаем профиль или создаем его, если он по какой-то причине отсутствует
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {e}")
        messages.error(request, "❌ Ошибка доступа к данным профиля.")
        return redirect("accounts:profile")

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if u_form.is_valid() and p_form.is_valid():
            with transaction.atomic():
                u_form.save()
                p_form.save()
            messages.success(request, "✅ Данные успешно обновлены!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "❌ Исправьте ошибки в форме.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "breadcrumbs": get_breadcrumbs([
            ("Личный кабинет", reverse("accounts:profile"), "fas fa-user"),
            ("Настройки профиля", None, "fas fa-user-cog"),
        ])
    }
    return render(request, "accounts/profile_update.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def password_change(request):
    """
    Смена пароля пользователя с автоматическим обновлением сессии,
    чтобы пользователя не разлогинило после смены пароля.
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                user = form.save()
                update_session_auth_hash(request, user)  # Важно для сохранения сессии
                messages.success(request, "✅ Пароль успешно изменен!")
                return redirect("accounts:profile")
            except Exception as e:
                logger.error(f"Ошибка смены пароля: {e}")
                messages.error(
                    request, "❌ Ошибка при смене пароля. Обратитесь к администратору."
                )
        else:
            messages.error(
                request, "❌ Пожалуйста, проверьте правильность ввода паролей."
            )
    else:
        form = CustomPasswordChangeForm(request.user)

    context = {
        "form": form,
        "breadcrumbs": get_breadcrumbs([
            ("Личный кабинет", reverse("accounts:profile"), "fas fa-user"),
            ("Смена пароля", None, "fas fa-key"),
        ])
    }
    return render(request, "accounts/password_change.html", context)


@login_required
def ticket_list(request):
    """
    Отображение списка всех обращений текущего пользователя.
    """
    try:
        # Получаем тикеты пользователя с предзагрузкой связанных данных
        tickets = (
            Ticket.objects.filter(user=request.user)
            .select_related("user")
            .order_by("-created_at")
        )
        context = {
            "tickets": tickets,
            "breadcrumbs": get_breadcrumbs([
                ("Личный кабинет", reverse("accounts:profile"), "fas fa-user"),
                ("Техподдержка", None, "fas fa-ticket-alt"),
            ])
        }
        return render(request, "accounts/ticket_list.html", context)
    except Exception as e:
        logger.error(f"Ошибка загрузки списка тикетов: {e}")
        messages.error(request, "❌ Ошибка загрузки ваших обращений.")
        return redirect("accounts:profile")


@login_required
@require_http_methods(["GET", "POST"])
def ticket_detail(request, pk):
    """
    Детальная страница тикета с историей переписки и возможностью ответа.
    Доступ имеют авторы тикета и сотрудники (is_staff).
    """
    try:
        # Сотрудники видят все тикеты, обычные пользователи - только свои
        if request.user.is_staff:
            ticket = get_object_or_404(Ticket.objects.select_related("user"), pk=pk)
        else:
            ticket = get_object_or_404(
                Ticket.objects.select_related("user"), pk=pk, user=request.user
            )

        if request.method == "POST":
            form = TicketResponseForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    response = form.save(commit=False)
                    response.ticket = ticket
                    response.user = request.user
                    # Флаг is_admin_response проставляется в модели TicketResponse.save()
                    response.save()

                    # Переводим тикет в статус "В обработке", если отвечает пользователь
                    if not request.user.is_staff:
                        ticket.status = Ticket.STATUS_IN_PROGRESS

                    ticket.save()

                messages.success(request, "✅ Ответ успешно добавлен!")
                return redirect("accounts:ticket_detail", pk=pk)
            else:
                messages.error(request, "❌ Сообщение слишком короткое или пустое.")
        else:
            form = TicketResponseForm()

        # История переписки (все ответы к тикету)
        responses = ticket.responses.select_related("user").order_by("created_at")

        context = {
            "ticket": ticket,
            "responses": responses,
            "form": form,
            "title": f"Тикет #{ticket.id}",
            "breadcrumbs": get_breadcrumbs([
                ("Личный кабинет", reverse("accounts:profile"), "fas fa-user"),
                ("Техподдержка", reverse("accounts:ticket_list"), "fas fa-ticket-alt"),
                (f"Тикет #{ticket.id}", None, "fas fa-info-circle"),
            ])
        }
        return render(request, "accounts/ticket_detail.html", context)

    except Exception as e:
        logger.error(f"Ошибка загрузки тикета #{pk}: {e}")
        messages.error(request, "❌ Не удалось загрузить обращение.")
        return redirect("accounts:ticket_list")


@login_required
@require_http_methods(["GET", "POST"])
def create_ticket(request):
    """
    Создание нового обращения в службу поддержки.
    """
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    ticket = form.save(commit=False)
                    ticket.user = request.user
                    ticket.save()
                messages.success(
                    request, "✅ Ваше обращение принято и скоро будет рассмотрено!"
                )
                return redirect("accounts:ticket_detail", pk=ticket.pk)
            except Exception as e:
                logger.error(f"Ошибка при создании тикета: {e}")
                messages.error(request, "❌ Критическая ошибка при создании тикета.")
        else:
            messages.error(request, "❌ Пожалуйста, заполните тему и сообщение.")
    else:
        form = TicketForm()

    context = {
        "form": form,
        "breadcrumbs": get_breadcrumbs([
            ("Личный кабинет", reverse("accounts:profile"), "fas fa-user"),
            ("Техподдержка", reverse("accounts:ticket_list"), "fas fa-ticket-alt"),
            ("Новое обращение", None, "fas fa-plus"),
        ])
    }
    return render(request, "accounts/create_ticket.html", context)


@login_required
def logout_confirmation(request):
    """
    Страница с подтверждением выхода из системы для предотвращения случайного выхода.
    """
    context = {
        "breadcrumbs": get_breadcrumbs([
            ("Выход", None, "fas fa-sign-out-alt"),
        ])
    }
    return render(request, "accounts/logout_confirm.html", context)


@require_http_methods(["POST"])
def custom_logout(request):
    """
    Обработка выхода (только через POST для безопасности).
    """
    try:
        logout(request)
        messages.success(request, "✅ Вы успешно вышли из системы. До свидания!")
        return redirect(getattr(settings, "LOGOUT_REDIRECT_URL", "main:index"))
    except Exception as e:
        logger.error(f"Ошибка при выходе: {e}")
        messages.error(request, "❌ Произошла ошибка при выходе.")
        return redirect("main:index")


@login_required
def profile_view(request):
    """
    Главная страница личного кабинета со статистикой пользователя.
    """
    try:
        user = request.user
        # Считаем количество активных тикетов
        tickets_count = Ticket.objects.filter(user=user).count()

        # Получаем статистику из других приложений
        reviews_count = get_reviews_count(user)
        comments_count = get_comments_count(user)

        context = {
            "tickets_count": tickets_count,
            "reviews_count": reviews_count,
            "comments_count": comments_count,
            "title": "Мой профиль",
            "breadcrumbs": get_breadcrumbs([
                ("Личный кабинет", None, "fas fa-user"),
            ])
        }
        return render(request, "accounts/profile.html", context)

    except Exception as e:
        logger.error(f"Ошибка загрузки личного кабинета: {e}")
        messages.error(request, "❌ Не удалось загрузить данные профиля.")
        return redirect("main:index")
