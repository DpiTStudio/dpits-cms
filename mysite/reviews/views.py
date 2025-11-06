# reviews/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm


def review_list(request):
    """Представление для отображения списка одобренных отзывов"""
    try:
        reviews = Review.objects.filter(status="approved").order_by("-created_at")
    except Exception:
        reviews = []
    return render(request, "reviews/list.html", {"reviews": reviews})


def add_review(request):
    """Представление для добавления нового отзыва"""
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Ваш отзыв отправлен на модерацию. Спасибо!")
                return redirect("reviews:list")
            except Exception as e:
                messages.error(request, f"Произошла ошибка при сохранении отзыва: {str(e)}")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = ReviewForm()

    return render(request, "reviews/add.html", {"form": form})
