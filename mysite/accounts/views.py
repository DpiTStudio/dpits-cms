# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
import logging

from .models import Ticket, TicketResponse, UserProfile
from .forms import (
    UserRegisterForm,  # ИСПРАВЛЕНО: CustomUserCreationForm -> UserRegisterForm
    UserUpdateForm,
    ProfileUpdateForm,
    TicketForm,
    TicketResponseForm,
    CustomPasswordChangeForm,
    ProfileEditForm,  # ДОБАВЛЕНО: недостающий импорт
)

logger = logging.getLogger(__name__)


def register(request):
    """
    Регистрация нового пользователя с обработкой ошибок
    """
    if request.user.is_authenticated:
        messages.info(request, "Вы уже авторизованы!")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)  # ИСПРАВЛЕНО
        try:
            if form.is_valid():
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
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
        form = UserRegisterForm()  # ИСПРАВЛЕНО

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """
    Отображение профиля пользователя со статистикой
    """
    try:
        user = request.user
        tickets_count = Ticket.objects.filter(user=user).count()

        # Статистика из других приложений (с обработкой ошибок)
        reviews_count = get_reviews_count(user)
        comments_count = get_comments_count(user)

        context = {
            "tickets_count": tickets_count,
            "reviews_count": reviews_count,
            "comments_count": comments_count,
        }
        return render(request, "accounts/profile.html", context)

    except Exception as e:
        logger.error(f"Ошибка загрузки профиля: {e}")
        messages.error(request, "❌ Ошибка загрузки профиля")
        return redirect("accounts:profile")  # ИСПРАВЛЕНО: было main:index


def get_reviews_count(user):
    """Получение количества отзывов пользователя"""
    try:
        from reviews.models import Review

        return Review.objects.filter(author=user).count()
    except (ImportError, Exception):
        return 0


def get_comments_count(user):
    """Получение количества комментариев пользователя"""
    try:
        from comments.models import Comment

        return Comment.objects.filter(author=user).count()
    except (ImportError, Exception):
        return 0


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """
    Редактирование основных данных пользователя
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

    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def profile_update(request):
    """
    Расширенное редактирование профиля пользователя
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if u_form.is_valid() and p_form.is_valid():
            with transaction.atomic():
                u_form.save()
                p_form.save()
            messages.success(request, "✅ Профиль успешно обновлен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "❌ Исправьте ошибки в форме")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)

    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "accounts/profile_update.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def password_change(request):
    """
    Смена пароля пользователя
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "✅ Пароль успешно изменен!")
                return redirect("accounts:profile")
            except Exception as e:
                logger.error(f"Ошибка смены пароля: {e}")
                messages.error(request, "❌ Ошибка при смене пароля")
        else:
            messages.error(request, "❌ Исправьте ошибки в форме")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "accounts/password_change.html", {"form": form})


@login_required
def ticket_list(request):
    """
    Список тикетов пользователя
    """
    try:
        tickets = (
            Ticket.objects.filter(user=request.user)
            .select_related("user")
            .order_by("-created_at")
        )
        return render(request, "accounts/ticket_list.html", {"tickets": tickets})
    except Exception as e:
        logger.error(f"Ошибка загрузки тикетов: {e}")
        messages.error(request, "❌ Ошибка загрузки списка тикетов")
        return redirect("accounts:profile")


@login_required
@require_http_methods(["GET", "POST"])
def ticket_detail(request, pk):
    """
    Детальная страница тикета с ответами
    """
    try:
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
                    response.is_admin_response = request.user.is_staff
                    response.save()

                    # Обновляем статус и время тикета
                    if not request.user.is_staff:
                        ticket.status = "in_progress"
                    ticket.save()

                messages.success(request, "✅ Сообщение отправлено!")
                return redirect("accounts:ticket_detail", pk=pk)
            else:
                messages.error(request, "❌ Ошибка в форме ответа")
        else:
            form = TicketResponseForm()

        responses = ticket.responses.select_related("user").order_by("created_at")

        context = {"ticket": ticket, "responses": responses, "form": form}
        return render(request, "accounts/ticket_detail.html", context)

    except Exception as e:
        logger.error(f"Ошибка загрузки тикета: {e}")
        messages.error(request, "❌ Ошибка загрузки тикета")
        return redirect("accounts:ticket_list")


@login_required
@require_http_methods(["GET", "POST"])
def create_ticket(request):
    """
    Создание нового тикета
    """
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    ticket = form.save(commit=False)
                    ticket.user = request.user
                    ticket.save()
                messages.success(request, "✅ Тикет создан успешно!")
                return redirect("accounts:ticket_detail", pk=ticket.pk)
            except Exception as e:
                logger.error(f"Ошибка создания тикета: {e}")
                messages.error(request, "❌ Ошибка создания тикета")
        else:
            messages.error(request, "❌ Исправьте ошибки в форме")
    else:
        form = TicketForm()

    return render(request, "accounts/create_ticket.html", {"form": form})


@login_required
def logout_confirmation(request):
    """
    Страница подтверждения выхода
    """
    return render(request, "accounts/logout_confirm.html")


@require_http_methods(["POST"])
def custom_logout(request):
    """
    Обработка выхода пользователя (только POST запросы)
    """
    try:
        logout(request)
        messages.success(request, "✅ Вы успешно вышли из системы!")
        return redirect(
            settings.LOGOUT_REDIRECT_URL
            if hasattr(settings, "LOGOUT_REDIRECT_URL")
            else "main:index"  # Или 'accounts:login' если хотите на страницу логина
        )
    except Exception as e:
        logger.error(f"Ошибка выхода: {e}")
        messages.error(request, "❌ Ошибка при выходе из системы")
        return redirect("main:index")
