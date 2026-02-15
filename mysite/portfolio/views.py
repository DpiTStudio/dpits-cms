# ============================================================================================= #
# ФАЙЛ: VIEWS.PY                                                                                #
# ОПИСАНИЕ:                                                                                     #
# Контроллеры (представления) приложения Портфолио. Отвечает за обработку запросов пользователей,#
# формирование контекста страниц и рендеринг шаблонов. Реализует публичную часть (каталог) и    #
# закрытую часть (личный кабинет клиента).                                                      #
#                                                                                               #
# НЮАНСЫ И ФУНКЦИОНАЛ:                                                                          #
# 1. Публичные разделы:                                                                         #
#    - PortfolioListView: Вывод списка работ с пагинацией и фильтрацией по категориям.          #
#      Использует кеширование категорий для оптимизации.                                        #
#    - PortfolioDetailView: Детальная страница работы. Подгружает отзывы и похожие проекты.     #
#      Инкрементирует счетчик просмотров.                                                       #
# 2. Личный кабинет клиента (доступен только авторизованным):                                   #
#    - client_dashboard: Сводная статистика по заказам клиента.                                 #
#    - order_list/order_detail: Управление заказами, просмотр статусов и переписка.             #
#    - client_profile: Редактирование профиля заказчика.                                        #
# 3. Функциональные особенности:                                                                #
#    - Использование миксинов и декораторов (@login_required, @user_passes_test) для защиты.    #
#    - Сложные выборки с prefetch_related/select_related для оптимизации SQL-запросов.          #
#    - Хлебные крошки (Breadcrumbs) формируются динамически для каждой страницы.                #
# ============================================================================================= #
# portfolio/views.py
# Представления (контроллеры) для приложения portfolio (портфолио)
from django.shortcuts import render, get_object_or_404, redirect, reverse
from main.breadcrumbs import get_breadcrumbs
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test  # Для гибкой проверки прав
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, Q
from django.contrib.auth import get_user_model  # Для безопасного получения модели User
from .models import (
    PortfolioCategory,
    PortfolioItem,
    Client,
    Order,
    OrderMessage,
    PortfolioReview,
)
from .forms import OrderForm, ReviewForm, ClientProfileForm

# Попытка импорта модели новостей
try:
    from news.models import News, NewsCategory
except ImportError:
    News = None
    NewsCategory = None  # Добавлено: явное определение, чтобы избежать NameError

User = get_user_model()


# --- Список работ портфолио ---
class PortfolioListView(ListView):
    """Список опубликованных работ портфолио с фильтрацией по категории."""

    model = PortfolioItem
    template_name = "portfolio/list.html"
    context_object_name = "portfolio_items"
    paginate_by = 12

    def get_queryset(self):
        queryset = PortfolioItem.objects.filter(status="published").select_related(
            "category", "client"
        )
        # Поиск по запросу
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(short_description__icontains=query) |
                Q(technologies__icontains=query)
            )

        # Фильтр по категории
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Сортировка
        sort_by = self.request.GET.get("sort", "-created_at")
        valid_sorts = {"created_at", "-created_at", "title", "-views"}
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by("-created_at")
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кэширование активных категорий
        cache_key = "portfolio_categories_active"
        categories = cache.get(cache_key)
        if not categories:
            categories = list(
                PortfolioCategory.objects.filter(is_active=True).order_by(
                    "-order", "name"
                )
            )
            cache.set(cache_key, categories, 600)  # 10 минут

        context["categories"] = categories
        context["selected_category"] = self.request.GET.get("category", "")
        context["current_sort"] = self.request.GET.get("sort", "-created_at")
        context["search_query"] = self.request.GET.get("q", "")
        context["recent_portfolio_list"] = (
            PortfolioItem.objects.filter(status="published")
            .select_related("category")
            .order_by("-created_at")[:3]
        )
        context["breadcrumbs"] = get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
        ])

        return context


# --- Детальная страница работы ---
class PortfolioDetailView(DetailView):
    """Детальный просмотр работы портфолио."""

    model = PortfolioItem
    template_name = "portfolio/detail.html"
    context_object_name = "item"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return PortfolioItem.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отзывы
        context["reviews"] = (
            PortfolioReview.objects.filter(portfolio_item=self.object, is_approved=True)
            .select_related("client", "client__user")
            .order_by("-created_at")
        )

        # Похожие работы
        context["related_works"] = (
            PortfolioItem.objects.filter(
                category=self.object.category, status="published"
            )
            .select_related("category", "client")
            .exclude(id=self.object.id)
            .order_by("-created_at")[:4]
        )

        # Для совместимости с hero.html и другими шаблонами
        context["portfolio_item"] = self.object
        context["categories"] = PortfolioCategory.objects.filter(is_active=True).order_by("-order", "name")

        # Счётчик просмотров
        self.object.increment_views()

        context["breadcrumbs"] = get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            (self.object.category.name, self.object.category.get_absolute_url()),
            (self.object.title, reverse("portfolio:detail", kwargs={"slug": self.object.slug})),
        ])

        return context


# --- Категория ---
class CategoryDetailView(DetailView):
    """Просмотр категории портфолио."""

    model = PortfolioCategory
    template_name = "portfolio/category_detail.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["portfolio_items"] = (
            PortfolioItem.objects.filter(category=self.object, status="published")
            .select_related("client")
            .order_by("-created_at")
        )
        context["breadcrumbs"] = get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            (self.object.name, self.object.get_absolute_url()),
        ])
        return context


def categories_view(request):
    """Все активные категории."""
    categories = PortfolioCategory.objects.filter(is_active=True).order_by(
        "-order", "name"
    )
    breadcrumbs = get_breadcrumbs([
        ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
        ("Категории", reverse("portfolio:categories")),
    ])
    return render(request, "portfolio/categories.html", {
        "categories": categories,
        "breadcrumbs": breadcrumbs
    })


# --- Профиль клиента ---
@login_required
def client_profile(request):
    """Управление профилем клиента."""
    client, created = Client.objects.get_or_create(user=request.user)  # Упрощение

    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()  # user уже связан, не нужно вручную присваивать
            messages.success(request, "Профиль успешно обновлён!")
            return redirect("portfolio:client_profile")
    else:
        form = ClientProfileForm(instance=client)

    context = {
        "form": form,
        "client": client,
        "breadcrumbs": get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            ("Профиль клиента", None, "fas fa-user-circle"),
        ])
    }
    return render(request, "portfolio/client_profile.html", context)


# --- Личный кабинет клиента ---
@login_required
def client_dashboard(request):
    """Обобщённая статистика по клиенту: заказы, отзывы."""
    try:
        client = Client.objects.select_related("user").get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, "Профиль клиента не найден.")
        return redirect("portfolio:client_profile")

    # Оптимизированные запросы
    orders = (
        Order.objects.filter(client=client)
        .select_related("client", "client__user")
        .order_by("-created_at")[:5]
    )
    reviews = (
        PortfolioReview.objects.filter(client=client)
        .select_related("portfolio_item", "portfolio_item__category")
        .order_by("-created_at")[:3]
    )

    # Агрегация для статистики
    stats = Order.objects.filter(client=client).aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        active=Count("id", filter=Q(status="in_progress")),
    )

    context = {
        "client": client,
        "orders": orders,
        "reviews": reviews,
        "orders_count": stats["total"] or 0,
        "completed_orders": stats["completed"] or 0,
        "active_orders": stats["active"] or 0,
        "breadcrumbs": get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            ("Личный кабинет клиента", None, "fas fa-tachometer-alt"),
        ])
    }
    return render(request, "portfolio/client_dashboard.html", context)


# --- Список заказов ---
@login_required
def order_list(request):
    """Полный список заказов клиента с фильтрацией."""
    try:
        client = Client.objects.select_related("user").get(user=request.user)
    except Client.DoesNotExist:
        messages.error(request, "Сначала заполните профиль клиента!")
        return redirect("portfolio:client_profile")

    orders = (
        Order.objects.filter(client=client)
        .select_related("client", "client__user")
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)

    stats = Order.objects.filter(client=client).aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        active=Count("id", filter=Q(status="in_progress")),
    )

    context = {
        "client": client,
        "orders": orders,
        "orders_count": stats["total"] or 0,
        "completed_orders": stats["completed"] or 0,
        "active_orders": stats["active"] or 0,
        "status_filter": status_filter,
        "breadcrumbs": get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            ("Личный кабинет", reverse("portfolio:client_dashboard"), "fas fa-tachometer-alt"),
            ("Мои заказы", None, "fas fa-shopping-cart"),
        ])
    }
    return render(request, "portfolio/order_list.html", context)


# --- Детали заказа ---
@login_required
def order_detail(request, pk):
    """Детали заказа и переписка."""
    order = get_object_or_404(
        Order.objects.select_related("client__user").prefetch_related("messages__user"),
        pk=pk,
        client__user=request.user,
    )

    if request.method == "POST" and "message" in request.POST:
        message_content = request.POST.get("message").strip()
        if message_content:
            OrderMessage.objects.create(
                order=order, user=request.user, message=message_content
            )
            messages.success(request, "Сообщение отправлено!")
            return redirect("portfolio:order_detail", pk=order.pk)

    context = {
        "order": order,
        "breadcrumbs": get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            ("Личный кабинет", reverse("portfolio:client_dashboard"), "fas fa-tachometer-alt"),
            ("Заказы", reverse("portfolio:order_list"), "fas fa-shopping-cart"),
            (f"Заказ #{order.id}", None, "fas fa-file-invoice"),
        ])
    }
    return render(request, "portfolio/order_detail.html", context)


# --- Создание заказа ---
@login_required
def create_order(request):
    """Создание нового заказа."""
    client, created = Client.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, "Создан профиль клиента. Теперь можно создавать заказы.")

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

    context = {
        "form": form,
        "breadcrumbs": get_breadcrumbs([
            ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
            ("Личный кабинет", reverse("portfolio:client_dashboard"), "fas fa-tachometer-alt"),
            ("Новый заказ", None, "fas fa-plus-circle"),
        ])
    }
    return render(request, "portfolio/create_order.html", context)


# --- Создание отзыва ---
@login_required
def create_review(request, slug):
    """Создание или редактирование отзыва на работу."""
    portfolio_item = get_object_or_404(PortfolioItem, slug=slug)
    client = get_object_or_404(Client, user=request.user)

    existing_review = PortfolioReview.objects.filter(
        client=client, portfolio_item=portfolio_item
    ).first()
    is_editing = existing_review is not None

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = client
            review.portfolio_item = portfolio_item
            review.save()
            messages.success(request, "Отзыв отправлен на модерацию!")
            return redirect("portfolio:detail", slug=portfolio_item.slug)
    else:
        form = ReviewForm(instance=existing_review)

    return render(
        request,
        "portfolio/create_review.html",
        {
            "form": form,
            "is_editing": is_editing,
            "breadcrumbs": get_breadcrumbs([
                ("Портфолио", reverse("portfolio:list"), "fas fa-layer-group"),
                (portfolio_item.title, portfolio_item.get_absolute_url()),
                ("Оставить отзыв", None, "fas fa-star"),
            ])
        },
    )


# --- Создание новости из портфолио ---
@login_required
@user_passes_test(
    lambda u: u.has_perm("news.add_news")
)  # Заменён на user_passes_test для гибкости
def create_news_from_portfolio(request, slug):
    """Создание новости на основе работы портфолио."""
    if not News or not NewsCategory:
        messages.error(request, "Приложение новостей не установлено.")
        return redirect("portfolio:detail", slug=slug)

    portfolio_item = get_object_or_404(PortfolioItem, slug=slug)

    try:
        category, _ = NewsCategory.objects.get_or_create(
            name="Портфолио",
            defaults={
                "slug": "portfolio",
                "description": "Новости о работах портфолио",
                "show_in_menu": True,
                "order": 10,
                "is_active": True,
            },
        )

        if News.objects.filter(slug=f"portfolio-{portfolio_item.slug}").exists():
            messages.info(request, "Новость для этой работы уже существует.")
            return redirect("news:detail", slug=f"portfolio-{portfolio_item.slug}")

        news = News.objects.create(
            title=f"Работа портфолио: {portfolio_item.title}",
            slug=f"portfolio-{portfolio_item.slug}",
            category=category,
            image=portfolio_item.image,
            short_description=portfolio_item.short_description[:200],
            content=portfolio_item.create_news_content(),
            is_active=True,
        )

        messages.success(request, "Новость успешно создана!")
        return redirect("news:detail", slug=news.slug)

    except Exception as e:
        messages.error(request, f"Ошибка при создании новости: {str(e)}")
        return redirect("portfolio:detail", slug=portfolio_item.slug)
