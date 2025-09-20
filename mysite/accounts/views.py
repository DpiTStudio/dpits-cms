# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from .models import Ticket, TicketResponse, UserProfile
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    TicketForm,
    TicketResponseForm,
    ProfileEditForm,
    CustomPasswordChangeForm,
)


def register(request):
    """
    Обработка регистрации нового пользователя
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно! Добро пожаловать!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """
    Отображение профиля пользователя со статистикой
    """
    # Получаем статистику пользователя
    tickets_count = Ticket.objects.filter(user=request.user).count()

    # Пытаемся импортировать модели из других приложений
    reviews_count = 0
    comments_count = 0

    try:
        from reviews.models import Review

        reviews_count = Review.objects.filter(author=request.user).count()
    except ImportError:
        pass
    except Exception as e:
        # Логируем ошибку, если нужно
        print(f"Error loading reviews: {e}")

    try:
        from comments.models import Comment

        comments_count = Comment.objects.filter(author=request.user).count()
    except ImportError:
        pass
    except Exception as e:
        # Логируем ошибку, если нужно
        print(f"Error loading comments: {e}")

    context = {
        "tickets_count": tickets_count,
        "reviews_count": reviews_count,
        "comments_count": comments_count,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
    """
    Редактирование основных данных пользователя
    """
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def profile_update(request):
    """
    Расширенное редактирование профиля пользователя
    """
    # Получаем или создаем профиль пользователя
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=user_profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "accounts/profile_update.html", context)


@login_required
def password_change(request):
    """
    Смена пароля пользователя
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "accounts/password_change.html", {"form": form})


@login_required
def ticket_list(request):
    """
    Список тикетов пользователя
    """
    tickets = Ticket.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/ticket_list.html", {"tickets": tickets})


@login_required
def ticket_detail(request, pk):
    """
    Детальная страница тикета с ответами
    """
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)

    if request.method == "POST":
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user
            response.is_admin_response = request.user.is_staff
            response.save()

            # Обновляем статус тикета если отвечает пользователь
            if not request.user.is_staff:
                ticket.status = "in_progress"
                ticket.save()

            messages.success(request, "Сообщение отправлено!")
            return redirect("accounts:ticket_detail", pk=pk)
    else:
        form = TicketResponseForm()

    responses = ticket.responses.all().order_by("created_at")

    context = {
        "ticket": ticket,
        "responses": responses,
        "form": form,
    }
    return render(request, "accounts/ticket_detail.html", context)


@login_required
def create_ticket(request):
    """
    Создание нового тикета
    """
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Тикет создан успешно!")
            return redirect("accounts:ticket_detail", pk=ticket.pk)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = TicketForm()

    return render(request, "accounts/create_ticket.html", {"form": form})


def logout_confirmation(request):
    """
    Страница подтверждения выхода
    """
    return render(request, "accounts/logout_confirm.html")


@require_POST
@csrf_protect
def custom_logout(request):
    """
    Обработка выхода пользователя
    """
    logout(request)
    messages.success(request, "Вы успешно вышли из системы!")
    return redirect(
        settings.LOGOUT_REDIRECT_URL
        if hasattr(settings, "LOGOUT_REDIRECT_URL")
        else "home"
    )
