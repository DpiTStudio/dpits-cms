# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Count
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
from django.contrib.auth import update_session_auth_hash


def register(request):
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
    # Получаем статистику пользователя
    try:
        from reviews.models import Review
        from comments.models import Comment

        tickets_count = Ticket.objects.filter(user=request.user).count()
        reviews_count = Review.objects.filter(user=request.user).count()
        comments_count = Comment.objects.filter(user=request.user).count()
    except ImportError:
        # Если приложения не установлены, используем значения по умолчанию
        tickets_count = Ticket.objects.filter(user=request.user).count()
        reviews_count = 0
        comments_count = 0

    context = {
        "tickets_count": tickets_count,
        "reviews_count": reviews_count,
        "comments_count": comments_count,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
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
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.userprofile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "accounts/profile_update.html", context)


@login_required
def password_change(request):
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
    tickets = Ticket.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/ticket_list.html", {"tickets": tickets})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)

    if request.method == "POST":
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.user = request.user
            response.is_admin_response = request.user.is_staff
            response.save()

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
