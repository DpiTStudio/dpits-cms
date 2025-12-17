# context_processors.py
# Контекстные процессоры для добавления данных в шаблоны
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page, LogStats


def site_settings(request):
    """
    Контекстный процессор для добавления настроек сайта в каждый шаблон.
    Использует кэширование для оптимизации производительности.
    """
    cache_key = "site_settings"
    settings = cache.get(cache_key)

    if not settings:
        # Получаем настройки из базы, если нет в кэше
        settings = SiteSettings.load()
        if settings:
            # Кэшируем на 5 минут (300 секунд)
            cache.set(cache_key, settings, 300)

    return {"site_settings": settings}


def menu_items(request):
    """
    Контекстный процессор для меню навигации.
    Кэширует список страниц для меню для улучшения производительности.
    """
    cache_key = "menu_pages"
    pages = cache.get(cache_key)

    if not pages:
        # Получаем страницы для меню из базы
        pages = Page.objects.filter(show_in_menu=True, show_on_site=True).order_by(
            "order", "title"
        )

        if pages:
            # Кэшируем на 10 минут (600 секунд)
            cache.set(cache_key, list(pages), 600)
        else:
            pages = []

    return {"menu_pages": pages}


def sidebar_data(request):
    """
    Контекстный процессор для данных сайдбара.
    Возвращает последние новости, работы портфолио и отзывы.
    Использует кэширование для оптимизации производительности.
    """
    cache_key = "sidebar_data"
    sidebar_data = cache.get(cache_key)

    if not sidebar_data:
        sidebar_data = {}

        # Получаем 3 последние новости
        try:
            from news.models import News
            sidebar_data["sidebar_news"] = list(
                News.objects.filter(is_active=True).order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_news"] = []

        # Получаем 3 последние работы из портфолио
        try:
            from portfolio.models import PortfolioItem
            sidebar_data["sidebar_portfolio"] = list(
                PortfolioItem.objects.filter(status="published")
                .order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_portfolio"] = []

        # Получаем 3 последних отзыва
        try:
            from reviews.models import Review
            sidebar_data["sidebar_reviews"] = list(
                Review.objects.filter(status="approved").order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_reviews"] = []

        # Кэшируем на 10 минут (600 секунд)
        cache.set(cache_key, sidebar_data, 600)

    return sidebar_data


def seo_context(request):
    """
    Контекстный процессор для базовых SEO-данных.
    Предоставляет общие SEO-настройки для всех страниц.
    """
    settings = SiteSettings.load()
    return {
        "default_seo_title": getattr(settings, "seo_title", ""),
        "default_seo_description": getattr(settings, "seo_description", ""),
        "default_seo_keywords": getattr(settings, "seo_keywords", ""),
    }


def admin_dashboard_stats(request):
    """
    Контекстный процессор для статистики админ-панели.
    Данные используются на главной странице админки (dashboard).
    """
    # Не считаем статистику для анонимных пользователей и не-админов
    if not request.user.is_authenticated or not request.path.startswith("/admin/"):
        return {}

    cache_key = "admin_dashboard_stats"
    stats = cache.get(cache_key)

    if stats is None:
        from django.contrib.auth import get_user_model
        from django.db.models import Sum

        User = get_user_model()

        # Импортируем модели внутри функции, чтобы избежать циклических импортов
        try:
            from news.models import News
        except Exception:
            News = None

        try:
            from portfolio.models import PortfolioItem, Order, PortfolioReview, Client
        except Exception:
            PortfolioItem = Order = PortfolioReview = Client = None

        try:
            from reviews.models import Review
        except Exception:
            Review = None

        try:
            from feedback.models import FeedbackMessage
        except Exception:
            FeedbackMessage = None

        try:
            from accounts.models import Ticket
        except Exception:
            Ticket = None

        # Базовая статистика пользователей
        total_users = User.objects.count()
        staff_users = User.objects.filter(is_staff=True).count()
        active_users = User.objects.filter(is_active=True).count()

        # Новости
        total_news = News.objects.count() if News else 0
        news_views = (
            News.objects.aggregate(total=Sum("views"))["total"] if News else 0
        ) or 0

        # Портфолио
        total_portfolio_items = PortfolioItem.objects.count() if PortfolioItem else 0
        portfolio_views = (
            PortfolioItem.objects.aggregate(total=Sum("views"))["total"]
            if PortfolioItem
            else 0
        ) or 0
        total_clients = Client.objects.count() if Client else 0
        total_orders = Order.objects.count() if Order else 0

        # Отзывы
        total_site_reviews = Review.objects.count() if Review else 0
        approved_site_reviews = (
            Review.objects.filter(status="approved").count() if Review else 0
        )
        total_portfolio_reviews = (
            PortfolioReview.objects.count() if PortfolioReview else 0
        )

        # Обратная связь
        total_feedback = FeedbackMessage.objects.count() if FeedbackMessage else 0
        new_feedback = (
            FeedbackMessage.objects.filter(status=FeedbackMessage.STATUS_NEW).count()
            if FeedbackMessage
            else 0
        )

        # Тикеты
        total_tickets = Ticket.objects.count() if Ticket else 0
        open_tickets = (
            Ticket.objects.filter(status=Ticket.STATUS_OPEN).count()
            if Ticket
            else 0
        )
        in_progress_tickets = (
            Ticket.objects.filter(status=Ticket.STATUS_IN_PROGRESS).count()
            if Ticket
            else 0
        )

        # Логи (используем последнюю запись LogStats + информацию из log_utils)
        last_log_stats = LogStats.objects.first()

        try:
            from .log_utils import get_log_file_info, get_error_log_file_info
        except Exception:
            get_log_file_info = get_error_log_file_info = None

        debug_log_info = get_log_file_info() if get_log_file_info else None
        error_log_info = (
            get_error_log_file_info() if get_error_log_file_info else None
        )

        stats = {
            "users": {
                "total": total_users,
                "staff": staff_users,
                "active": active_users,
            },
            "news": {
                "total": total_news,
                "views": news_views,
            },
            "portfolio": {
                "items": total_portfolio_items,
                "views": portfolio_views,
                "clients": total_clients,
                "orders": total_orders,
            },
            "reviews": {
                "site_total": total_site_reviews,
                "site_approved": approved_site_reviews,
                "portfolio_total": total_portfolio_reviews,
            },
            "feedback": {
                "total": total_feedback,
                "new": new_feedback,
            },
            "tickets": {
                "total": total_tickets,
                "open": open_tickets,
                "in_progress": in_progress_tickets,
            },
            "logs": {
                "last_stats": last_log_stats,
                "debug": debug_log_info,
                "error": error_log_info,
            },
        }

        # Кэшируем на 1 минуту, чтобы не нагружать БД
        cache.set(cache_key, stats, 60)

    return {"admin_stats": stats}
