# portfolio/views.py

from django.shortcuts import render, get_object_or_404
from .models import Portfolio, PortfolioCategory


def portfolio_list(request):
    portfolios = Portfolio.objects.filter(is_active=True).order_by("-created_at")
    categories = PortfolioCategory.objects.filter(is_active=True, show_in_menu=True)

    context = {
        "portfolios": portfolios,
        "categories": categories,
    }
    return render(request, "portfolio/list.html", context)


def portfolio_detail(request, slug):
    portfolio = get_object_or_404(Portfolio, slug=slug, is_active=True)
    portfolio.increment_views()

    similar_portfolios = (
        Portfolio.objects.filter(category=portfolio.category, is_active=True)
        .exclude(id=portfolio.id)
        .order_by("-created_at")[:4]
    )

    context = {
        "portfolio": portfolio,
        "similar_portfolios": similar_portfolios,
    }
    return render(request, "portfolio/detail.html", context)


def portfolio_by_category(request, slug):
    category = get_object_or_404(PortfolioCategory, slug=slug, is_active=True)
    portfolios = Portfolio.objects.filter(category=category, is_active=True).order_by(
        "-created_at"
    )
    categories = PortfolioCategory.objects.filter(is_active=True, show_in_menu=True)

    context = {
        "category": category,
        "portfolios": portfolios,
        "categories": categories,
    }
    return render(request, "portfolio/category.html", context)
