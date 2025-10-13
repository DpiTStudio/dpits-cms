# portfolio/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import (
    PortfolioCategory,
    PortfolioItem,
    Client,
    Order,
    OrderMessage,
    PortfolioReview,
)
from .forms import OrderForm, ReviewForm, ClientProfileForm


class PortfolioListView(ListView):
    """Список всех работ портфолио"""

    model = PortfolioItem
    template_name = "portfolio/list.html"
    context_object_name = "portfolio_items"
    paginate_by = 12

    def get_queryset(self):
        """Фильтрация работ по статусу и категории"""
        queryset = PortfolioItem.objects.filter(status="published")

        # Фильтрация по категории
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset.select_related("category", "client")

    def get_context_data(self, **kwargs):
        """Добавление категорий в контекст"""
        context = super().get_context_data(**kwargs)
        context["categories"] = PortfolioCategory.objects.filter(is_active=True)
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class PortfolioDetailView(DetailView):
    """Детальная страница работы портфолио"""

    model = PortfolioItem
    template_name = "portfolio/detail.html"
    context_object_name = "portfolio_item"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Только опубликованные работы"""
        return PortfolioItem.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        """Добавление отзывов и связанных работ в контекст"""
        context = super().get_context_data(**kwargs)

        # Отзывы к этой работе
        context["reviews"] = PortfolioReview.objects.filter(
            portfolio_item=self.object, is_approved=True
        ).select_related("client")

        # Похожие работы из той же категории
        context["related_works"] = PortfolioItem.objects.filter(
            category=self.object.category, status="published"
        ).exclude(id=self.object.id)[:4]

        # Увеличиваем счетчик просмотров
        self.object.increment_views()

        return context


class CategoryDetailView(DetailView):
    """Детальная страница категории"""

    model = PortfolioCategory
    template_name = "portfolio/category_detail.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        """Добавление работ категории в контекст"""
        context = super().get_context_data(**kwargs)
        context["portfolio_items"] = PortfolioItem.objects.filter(
            category=self.object, status="published"
        )
        return context


def categories_view(request):
    """Страница всех категорий"""
    categories = PortfolioCategory.objects.filter(is_active=True)
    return render(request, "portfolio/categories.html", {"categories": categories})


@login_required
def client_profile(request):
    """Профиль клиента"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        client = None

    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("portfolio:client_profile")
    else:
        form = ClientProfileForm(instance=client)

    return render(
        request, "portfolio/client_profile.html", {"form": form, "client": client}
    )


@login_required
def client_dashboard(request):
    """Личный кабинет клиента"""
    try:
        client = Client.objects.get(user=request.user)
        orders = Order.objects.filter(client=client)[:5]
        reviews = PortfolioReview.objects.filter(client=client)[:3]

        orders_count = Order.objects.filter(client=client).count()
        completed_orders = Order.objects.filter(
            client=client, status="completed"
        ).count()
        active_orders = Order.objects.filter(
            client=client, status="in_progress"
        ).count()

    except Client.DoesNotExist:
        client = None
        orders = []
        reviews = []
        orders_count = 0
        completed_orders = 0
        active_orders = 0

    return render(
        request,
        "portfolio/client_dashboard.html",
        {
            "client": client,
            "orders": orders,
            "reviews": reviews,
            "orders_count": orders_count,
            "completed_orders": completed_orders,
            "active_orders": active_orders,
        },
    )


@login_required
def order_detail(request, pk):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, pk=pk, client__user=request.user)

    if request.method == "POST":
        if "message" in request.POST:
            # Обработка нового сообщения
            message_content = request.POST.get("content")
            if message_content:
                OrderMessage.objects.create(
                    order=order, user=request.user, message=message_content
                )
                messages.success(request, "Сообщение отправлено!")
                return redirect("portfolio:order_detail", pk=order.pk)

    return render(request, "portfolio/order_detail.html", {"order": order})


@login_required
def create_order(request):
    """Создание нового заказа"""
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, "Сначала заполните профиль клиента!")
        return redirect("portfolio:client_profile")

    if request.method == "POST":
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client
            order.save()
            messages.success(request, "Заказ успешно создан!")
            return redirect("portfolio:order_detail", pk=order.pk)
    else:
        form = OrderForm()

    return render(request, "portfolio/create_order.html", {"form": form})


@login_required
def create_review(request, slug):
    """Создание отзыва о работе"""
    portfolio_item = get_object_or_404(PortfolioItem, slug=slug)
    client = get_object_or_404(Client, user=request.user)

    # Проверяем, есть ли уже отзыв от этого клиента
    existing_review = PortfolioReview.objects.filter(
        client=client, portfolio_item=portfolio_item
    ).first()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = client
            review.portfolio_item = portfolio_item
            review.save()
            messages.success(request, "Отзыв успешно отправлен на модерацию!")
            return redirect("portfolio:detail", slug=portfolio_item.slug)
    else:
        form = ReviewForm(instance=existing_review)

    return render(
        request,
        "portfolio/create_review.html",
        {"form": form, "portfolio_item": portfolio_item},
    )
