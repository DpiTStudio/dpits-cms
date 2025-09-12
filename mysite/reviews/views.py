# reviews/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm


def review_list(request):
    reviews = Review.objects.filter(status="approved").order_by("-created_at")
    return render(request, "reviews/list.html", {"reviews": reviews})


def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш отзыв отправлен на модерацию. Спасибо!")
            return redirect("reviews:list")
    else:
        form = ReviewForm()

    return render(request, "reviews/add.html", {"form": form})
