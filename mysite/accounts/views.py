# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    TicketForm,
    TicketResponseForm,
)
from .models import Ticket, TicketResponse


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("accounts:profile")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
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
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "accounts/profile.html", context)


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
            response.save()

            if not request.user.is_staff:
                ticket.status = "in_progress"
                ticket.save()

            messages.success(request, "Сообщение отправлено!")
            return redirect("accounts:ticket_detail", pk=pk)
    else:
        form = TicketResponseForm()

    responses = TicketResponse.objects.filter(ticket=ticket).order_by("created_at")

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
        form = TicketForm()

    return render(request, "accounts/create_ticket.html", {"form": form})
