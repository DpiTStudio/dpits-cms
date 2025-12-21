# portfolio/views.py
# Представления (контроллеры) для приложения portfolio (портфолио)
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)  # Импорт функций для рендеринга шаблонов, получения объектов и перенаправления
from django.views.generic import (
    ListView,
    DetailView,
)  # Импорт базовых классов представлений Django
from django.contrib.auth.decorators import (
    login_required,
)  # Декоратор для требования аутентификации
from django.contrib import messages  # Импорт системы сообщений Django
from django.core.cache import cache  # Импорт кэша для оптимизации производительности
from django.db.models import (
    Count,
    Q,
)  # Импорт функций агрегации и Q-объекта для сложных запросов
from .models import (
    PortfolioCategory,  # Модель категории портфолио
    PortfolioItem,  # Модель работы портфолио
    Client,  # Модель клиента
    Order,  # Модель заказа
    OrderMessage,  # Модель сообщения в заказе
    PortfolioReview,  # Модель отзыва о работе
)
from .forms import (
    OrderForm,
    ReviewForm,
    ClientProfileForm,
)  # Импорт форм для работы с заказами, отзывами и профилем клиента

# Импорт модели новостей (если приложение news установлено)
try:
    from news.models import News  # Пытаемся импортировать модель новостей
except ImportError:  # Если импорт не удался
    News = None  # Устанавливаем News в None


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

        return queryset.select_related("category", "client").order_by("-created_at")

    def get_context_data(self, **kwargs):
        """
        Добавление категорий в контекст.
        Оптимизировано с использованием кэширования.

        Args:
            **kwargs: Дополнительные аргументы контекста

        Returns:
            dict: Контекст для шаблона с категориями и выбранной категорией
        """
        context = super().get_context_data(**kwargs)  # Получаем базовый контекст

        # ИСПРАВЛЕНО: Используем кэш для категорий
        cache_key = "portfolio_categories_active"
        categories = cache.get(cache_key)
        if not categories:
            categories = list(
                PortfolioCategory.objects.filter(is_active=True).order_by(
                    "-order", "name"
                )
            )
            cache.set(cache_key, categories, 600)  # Кэш на 10 минут

        context["categories"] = categories  # Добавляем категории в контекст
        context["selected_category"] = self.request.GET.get(
            "category", ""
        )  # Получаем выбранную категорию из GET-параметра

        # Список последних работ для отображения внизу на всю ширину
        context["recent_portfolio_list"] = PortfolioItem.objects.filter(
            status="published"
        ).order_by("-created_at")[:3]

        return context  # Возвращаем контекст


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
        """
        Добавление отзывов и связанных работ в контекст.
        Оптимизировано с использованием select_related и prefetch_related.

        Args:
            **kwargs: Дополнительные аргументы контекста

        Returns:
            dict: Контекст для шаблона с отзывами и похожими работами
        """
        context = super().get_context_data(**kwargs)  # Получаем базовый контекст

        # Отзывы к этой работе
        # ИСПРАВЛЕНО: Добавлен select_related для оптимизации запросов к клиенту
        context["reviews"] = (
            PortfolioReview.objects.filter(portfolio_item=self.object, is_approved=True)
            .select_related(
                "client", "client__user"
            )  # Оптимизация: загружаем клиента и пользователя одним запросом
            .order_by("-created_at")  # Сортируем по дате создания (новые сверху)
        )

        # Похожие работы из той же категории
        # ИСПРАВЛЕНО: Добавлен select_related для оптимизации
        context["related_works"] = (
            PortfolioItem.objects.filter(
                category=self.object.category, status="published"
            )
            .select_related(
                "category", "client"
            )  # Оптимизация: загружаем категорию и клиента одним запросом
            .exclude(id=self.object.id)  # Исключаем текущую работу из списка похожих
            .order_by("-created_at")[
                :4
            ]  # Получаем 4 последние работы из той же категории
        )

        # Увеличиваем счетчик просмотров
        self.object.increment_views()  # Увеличиваем счетчик просмотров на 1

        return context  # Возвращаем контекст


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
        ).order_by("-created_at")
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


@login_required  # Декоратор: требует аутентификации пользователя
def client_dashboard(request):
    """
    Личный кабинет клиента.
    Отображает статистику и последние заказы и отзывы клиента.
    Оптимизировано с использованием select_related и агрегации.

    Args:
        request: HTTP-запрос от аутентифицированного пользователя

    Returns:
        HttpResponse: Отрендеренный шаблон личного кабинета клиента
    """
    try:
        # Получаем клиента по пользователю
        # ИСПРАВЛЕНО: Добавлен select_related для оптимизации
        client = Client.objects.select_related("user").get(user=request.user)

        # Последние 5 заказов клиента
        # ИСПРАВЛЕНО: Добавлен select_related и ограничение запроса
        orders = (
            Order.objects.filter(client=client)
            .select_related(
                "client", "client__user"
            )  # Оптимизация: загружаем клиента одним запросом
            .order_by("-created_at")[:5]  # Получаем только 5 последних заказов
        )

        # Последние 3 отзыва клиента
        # ИСПРАВЛЕНО: Добавлен select_related
        reviews = (
            PortfolioReview.objects.filter(client=client)
            .select_related(
                "client", "portfolio_item", "portfolio_item__category"
            )  # Оптимизация: загружаем связанные объекты
            .order_by("-created_at")[:3]  # Получаем только 3 последних отзыва
        )

        # Статистика заказов
        # ИСПРАВЛЕНО: Используем агрегацию для оптимизации запросов
        orders_stats = Order.objects.filter(client=client).aggregate(
            total=Count("id"),  # Общее количество заказов
            completed=Count(
                "id", filter=Q(status="completed")
            ),  # Количество завершенных заказов
            active=Count(
                "id", filter=Q(status="in_progress")
            ),  # Количество активных заказов
        )

        orders_count = orders_stats["total"] or 0  # Общее количество заказов
        completed_orders = (
            orders_stats["completed"] or 0
        )  # Количество завершенных заказов
        active_orders = orders_stats["active"] or 0  # Количество активных заказов

    except Client.DoesNotExist:  # Если клиент не найден
        client = None  # Устанавливаем клиента в None
        orders = []  # Пустой список заказов
        reviews = []  # Пустой список отзывов
        orders_count = 0  # Количество заказов = 0
        completed_orders = 0  # Количество завершенных заказов = 0
        active_orders = 0  # Количество активных заказов = 0

    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "portfolio/client_dashboard.html",  # Путь к шаблону
        {
            "client": client,  # Объект клиента
            "orders": orders,  # Список последних заказов
            "reviews": reviews,  # Список последних отзывов
            "orders_count": orders_count,  # Общее количество заказов
            "completed_orders": completed_orders,  # Количество завершенных заказов
            "active_orders": active_orders,  # Количество активных заказов
        },
    )  # Рендерим шаблон личного кабинета


@login_required  # Декоратор: требует аутентификации пользователя
def order_list(request):
    """
    Список всех заказов клиента.
    Оптимизировано с использованием select_related и агрегации.

    Args:
        request: HTTP-запрос от аутентифицированного пользователя

    Returns:
        HttpResponse: Отрендеренный шаблон со списком заказов или редирект на профиль
    """
    try:
        # Получаем клиента по пользователю
        # ИСПРАВЛЕНО: Добавлен select_related для оптимизации
        client = Client.objects.select_related("user").get(user=request.user)

        # Получаем все заказы клиента
        # ИСПРАВЛЕНО: Добавлен select_related
        orders = (
            Order.objects.filter(client=client)
            .select_related(
                "client", "client__user"
            )  # Оптимизация: загружаем клиента одним запросом
            .order_by("-created_at")  # Сортируем по дате создания (новые сверху)
        )

        # Фильтрация по статусу
        status_filter = request.GET.get(
            "status"
        )  # Получаем фильтр статуса из GET-параметра
        if status_filter:  # Если фильтр указан
            orders = orders.filter(status=status_filter)  # Фильтруем заказы по статусу

        # Статистика заказов
        # ИСПРАВЛЕНО: Используем агрегацию для оптимизации запросов
        orders_stats = Order.objects.filter(client=client).aggregate(
            total=Count("id"),  # Общее количество заказов
            completed=Count(
                "id", filter=Q(status="completed")
            ),  # Количество завершенных заказов
            active=Count(
                "id", filter=Q(status="in_progress")
            ),  # Количество активных заказов
        )

        orders_count = orders_stats["total"] or 0  # Общее количество заказов
        completed_orders = (
            orders_stats["completed"] or 0
        )  # Количество завершенных заказов
        active_orders = orders_stats["active"] or 0  # Количество активных заказов

    except Client.DoesNotExist:  # Если клиент не найден
        client = None  # Устанавливаем клиента в None
        orders = []  # Пустой список заказов
        orders_count = 0  # Количество заказов = 0
        completed_orders = 0  # Количество завершенных заказов = 0
        active_orders = 0  # Количество активных заказов = 0
        status_filter = None  # Фильтр статуса = None
        messages.error(
            request, "Сначала заполните профиль клиента!"
        )  # Показываем сообщение об ошибке
        return redirect(
            "portfolio:client_profile"
        )  # Перенаправляем на страницу профиля клиента

    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "portfolio/order_list.html",  # Путь к шаблону
        {
            "client": client,  # Объект клиента
            "orders": orders,  # Список заказов
            "orders_count": orders_count,  # Общее количество заказов
            "completed_orders": completed_orders,  # Количество завершенных заказов
            "active_orders": active_orders,  # Количество активных заказов
            "status_filter": status_filter,  # Выбранный фильтр статуса
        },
    )  # Рендерим шаблон со списком заказов


@login_required  # Декоратор: требует аутентификации пользователя
def order_detail(request, pk):
    """
    Детальная страница заказа.
    Отображает информацию о заказе и сообщения по заказу.
    Оптимизировано с использованием select_related и prefetch_related.

    Args:
        request: HTTP-запрос от аутентифицированного пользователя
        pk: Первичный ключ заказа

    Returns:
        HttpResponse: Отрендеренный шаблон с детальной информацией о заказе
    """
    # Получаем заказ или показываем ошибку 404
    # ИСПРАВЛЕНО: Добавлен select_related и prefetch_related для оптимизации
    order = get_object_or_404(
        Order.objects.select_related(
            "client", "client__user"
        ).prefetch_related(  # Оптимизация: загружаем клиента одним запросом
            "messages", "messages__user"
        ),  # Оптимизация: загружаем сообщения одним запросом
        pk=pk,
        client__user=request.user,  # Проверяем, что заказ принадлежит текущему пользователю
    )

    if request.method == "POST":  # Если запрос методом POST
        if "message" in request.POST:  # Если в запросе есть поле "message"
            # Обработка нового сообщения
            message_content = request.POST.get("message")  # Получаем текст сообщения
            if message_content:  # Если сообщение не пустое
                # Создаем новое сообщение
                OrderMessage.objects.create(
                    order=order,  # Связываем сообщение с заказом
                    user=request.user,  # Устанавливаем автора сообщения
                    message=message_content,  # Устанавливаем текст сообщения
                )
                messages.success(
                    request, "Сообщение отправлено!"
                )  # Показываем сообщение об успехе
                return redirect(
                    "portfolio:order_detail", pk=order.pk
                )  # Перенаправляем на страницу заказа

    # Формируем данные для шаблона
    return render(
        request,  # HTTP-запрос
        "portfolio/order_detail.html",  # Путь к шаблону
        {"order": order},  # Объект заказа с предзагруженными сообщениями
    )  # Рендерим шаблон с детальной информацией о заказе


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
