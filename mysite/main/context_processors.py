# context_processors.py
# КОНТЕКСТНЫЕ ПРОЦЕССОРЫ ДЛЯ ДОБАВЛЕНИЯ ДАННЫХ В ШАБЛОНЫ
#
# Этот файл содержит функции, которые автоматически добавляют определенные данные
# во все шаблоны (или в зависимости от условий).
# Это избавляет от необходимости передавать одни и те же данные в каждом представлении (view).

from datetime import datetime
from django.core.cache import cache  # Система кэширования
from .models import SiteSettings, Page, LogStats  # Импорт моделей из текущего приложения
from .admin_utils import format_bytes  # Утилита для форматирования байтов в читаемый вид (KB, MB, GB)


def site_settings(request):
    """
    Контекстный процессор для добавления настроек сайта в шаблоны.
    Позволяет использовать {{ site_settings.field_name }} в любом шаблоне.
    """
    cache_key = "site_settings"  # Ключ для хранения настроек в кэше
    settings = cache.get(cache_key)  # Пытаемся получить данные из кэша

    if not isinstance(settings, SiteSettings):
        # Если в кэше пусто, загружаем из базы данных
        settings = SiteSettings.load()
        if settings:
            # Если настройки найдены, сохраняем их в кэш на 5 минут (300 секунд)
            cache.set(cache_key, settings, 300)
    
    # Возвращаем словарь, который будет объединен с контекстом шаблона
    return {"site_settings": settings}


def menu_items(request):
    """
    Контекстный процессор для добавления страниц меню в шаблоны.
    Извлекает активные страницы, помеченные флажком show_in_menu.
    """
    cache_key = "menu_pages"  # Ключ кэша для страниц меню
    pages = cache.get(cache_key)  # Пытаемся получить список из кэша

    if not pages:
        # Если в кэше нет, выбираем страницы из БД
        pages = Page.objects.filter(show_in_menu=True, show_on_site=True).order_by(
            "order", "title"
        )
        if pages:
            # Сохраняем результат в кэш на 10 минут (600 секунд)
            # Мы преобразуем QuerySet в список, чтобы его можно было закешировать корректно
            cache.set(cache_key, list(pages), 600)
        else:
            pages = []
    
    return {"menu_pages": pages}


def dynamic_menus(request):
    """
    Контекстный процессор для динамических меню (категории услуг, портфолио и т.д.).
    """
    cache_key = "dynamic_menus_data"
    menus_data = cache.get(cache_key)

    if not isinstance(menus_data, dict):
        menus_data = {
            "service_categories": [],
            "portfolio_categories": [],
            "news_categories": [],
            "kb_categories": [],
        }

        # 1. Категории услуг
        try:
            from services.models import ServiceCategory
            menus_data["service_categories"] = list(
                ServiceCategory.objects.filter(is_active=True, show_in_menu=True).order_by("order", "name")
            )
        except (ImportError, AttributeError):
            pass

        # 2. Категории портфолио
        try:
            from portfolio.models import PortfolioCategory
            menus_data["portfolio_categories"] = list(
                PortfolioCategory.objects.filter(is_active=True).order_by("order", "name")
            )
        except (ImportError, AttributeError):
            pass

        # 3. Категории новостей
        try:
            from news.models import NewsCategory
            menus_data["news_categories"] = list(
                NewsCategory.objects.filter(is_active=True, show_in_menu=True).order_by("order", "name")
            )
        except (ImportError, AttributeError):
            pass

        # 4. Категории базы знаний
        try:
            from knowledge_base.models import Category as KBCategory
            menus_data["kb_categories"] = list(
                KBCategory.objects.all().order_by("order", "name")
            )
        except (ImportError, AttributeError):
            pass

        # Кэшируем на 10 минут
        cache.set(cache_key, menus_data, 600)

    return menus_data


def sidebar_data(request):
    """
    Контекстный процессор для данных сайдбара (боковой панели).
    Собирает последние новости, работы портфолио и отзывы.
    Использует общие кэш-ключи с IndexView для исключения дублирующихся запросов к БД.
    """
    cache_key = "sidebar_data"
    sidebar_data = cache.get(cache_key)

    if not isinstance(sidebar_data, dict):
        sidebar_data = {}
        # Динамический импорт моделей других приложений
        # Используется try-except, чтобы сайт не падал, если какое-то приложение не установлено
        try:
            from news.models import News
            # Общий кэш-ключ с IndexView — избегаем двойного запроса
            latest_news = cache.get("latest_news_3")
            if latest_news is None:
                latest_news = list(News.objects.filter(is_active=True).order_by("-created_at")[:3])
                cache.set("latest_news_3", latest_news, 300)
            sidebar_data["sidebar_news"] = latest_news
        except (ImportError, AttributeError):
            sidebar_data["sidebar_news"] = []

        try:
            from portfolio.models import PortfolioItem
            # Общий кэш-ключ с IndexView — избегаем двойного запроса
            latest_portfolio = cache.get("latest_portfolio_3")
            if latest_portfolio is None:
                latest_portfolio = list(PortfolioItem.objects.all().order_by("-created_at")[:3])
                cache.set("latest_portfolio_3", latest_portfolio, 300)
            sidebar_data["sidebar_portfolio"] = latest_portfolio
        except (ImportError, AttributeError):
            sidebar_data["sidebar_portfolio"] = []

        try:
            from reviews.models import Review
            # Получаем 2 последних одобренных отзыва
            sidebar_data["sidebar_reviews"] = list(
                Review.objects.filter(status='approved').order_by("-created_at")[:2]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_reviews"] = []

        # Кэшируем собранные данные на 5 минут
        cache.set(cache_key, sidebar_data, 300)

    return sidebar_data


def seo_context(request):
    """
    Добавляет базовую SEO-информацию из глобальных настроек сайта.
    Использует кэш чтобы не делать лишний запрос к БД на каждый HTTP-запрос.
    """
    settings = cache.get("site_settings") or SiteSettings.load()
    return {
        "default_seo_title": getattr(settings, "seo_title", ""),
        "default_seo_description": getattr(settings, "seo_description", ""),
        "default_seo_keywords": getattr(settings, "seo_keywords", ""),
    }


def admin_dashboard_stats(request):
    """
    Контекстный процессор для статистики админ-панели.
    Собирает метрики по всем сущностям (пользователи, новости, заказы и т.д.).
    Работает только для сотрудников (is_staff) при переходе в админку.
    """
    # Проверяем, является ли пользователь сотрудником и находится ли он в панели управления
    if not request.user.is_authenticated or not request.user.is_staff or not request.path.startswith("/admin/"):
        return {}

    cache_key = "admin_dashboard_stats"
    stats = cache.get(cache_key)

    if not stats:
        # 1. Статистика пользователей
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_users = User.objects.count()  # Общее количество
        staff_users = User.objects.filter(is_staff=True).count()  # Персонал
        active_users = User.objects.filter(is_active=True).count()  # Активные

        # 2. Новости
        total_news = 0
        news_views = 0
        try:
            from news.models import News
            total_news = News.objects.count()
            # Пытаемся получить сумму просмотров (если поле существует)
            from django.db.models import Sum
            news_views = News.objects.aggregate(Sum('views'))['views__sum'] or 0
        except (ImportError, Exception):
            pass

        # 3. Портфолио и Заказы
        total_portfolio_items = 0
        portfolio_views = 0
        total_clients = 0
        total_orders = 0
        try:
            from portfolio.models import PortfolioItem, Client, Order
            total_portfolio_items = PortfolioItem.objects.count()
            total_clients = Client.objects.count()
            total_orders = Order.objects.count()
            from django.db.models import Sum
            portfolio_views = PortfolioItem.objects.aggregate(Sum('views'))['views__sum'] or 0
        except (ImportError, Exception):
            pass

        # 4. Отзывы
        total_site_reviews = 0
        approved_site_reviews = 0
        total_portfolio_reviews = 0
        try:
            from reviews.models import Review
            total_site_reviews = Review.objects.count()
            # ИСПРАВЛЕНО: использование status='approved' вместо is_approved=True
            approved_site_reviews = Review.objects.filter(status='approved').count()
            
            # Также проверяем отзывы в портфолио
            try:
                from portfolio.models import PortfolioReview
                total_portfolio_reviews = PortfolioReview.objects.count()
            except ImportError:
                pass
        except (ImportError, Exception):
            pass

        # 5. Обратная связь (Сообщения)
        total_feedback = 0
        new_feedback = 0
        try:
            from feedback.models import FeedbackMessage
            total_feedback = FeedbackMessage.objects.count()
            # ИСПРАВЛЕНО: Запрос по статусу вместо свойства is_read
            new_feedback = FeedbackMessage.objects.filter(status=FeedbackMessage.STATUS_NEW).count()
        except (ImportError, Exception):
            pass

        # 6. Тикеты техподдержки
        total_tickets = 0
        open_tickets = 0
        in_progress_tickets = 0
        try:
            from accounts.models import Ticket
            total_tickets = Ticket.objects.count()
            open_tickets = Ticket.objects.filter(status='open').count()
            in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
        except (ImportError, Exception):
            pass

        # 7. Недавние записи для панелей управления
        recent_orders = []
        try:
            from portfolio.models import Order
            recent_orders = list(Order.objects.select_related('client__user').order_by('-created_at')[:5])
        except (ImportError, Exception):
            pass

        recent_feedback = []
        try:
            from feedback.models import FeedbackMessage
            recent_feedback = list(FeedbackMessage.objects.select_related('user').order_by('-created_at')[:5])
        except (ImportError, Exception):
            pass

        pending_reviews = []
        try:
            from reviews.models import Review
            pending_reviews = list(Review.objects.filter(status='pending').order_by('-created_at')[:5])
        except (ImportError, Exception):
            pass

        recent_logs = []
        try:
            from django.contrib.admin.models import LogEntry
            recent_logs = list(LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:10])
        except (ImportError, Exception):
            pass

        # 8. Управляющие параметры состояния
        maintenance_mode = False
        try:
            maintenance_mode = SiteSettings.load().site_closed
        except Exception:
            pass

        cache_backend = cache.__class__.__name__

        import os
        from django.conf import settings
        backup_dir = os.path.join(settings.BASE_DIR, "backups")
        backup_count = 0
        if os.path.exists(backup_dir):
            try:
                backup_count = len([f for f in os.listdir(backup_dir) if f.endswith('.sqlite3')])
            except Exception:
                pass

        # 9. Информация о логах приложений
        from .log_utils import get_log_file_info, get_error_log_file_info
        
        # Получаем данные о debug.log
        debug_log_info = get_log_file_info()
        # Получаем данные о error.log
        error_log_info = get_error_log_file_info()

        # Получаем последнюю запись статистики из БД
        last_log_stats = LogStats.objects.first()

        # 10. Системные характеристики сервера (CPU, Память, Версии)
        import sys
        import platform
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()  # Загрузка процессора в %
            memory = psutil.virtual_memory()
            memory_percent = memory.percent  # Использование памяти в %
            memory_used = format_bytes(memory.used)  # Занято (читаемо)
            memory_total = format_bytes(memory.total)  # Всего (читаемо)
            
            # Время аптайма системы (сколько сервер работает)
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_delta = datetime.now() - boot_time
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            uptime = f"{days}д {hours}ч {minutes}м"
        except Exception:
            # Если библиотека psutil не установлена или произошла ошибка
            cpu_percent = memory_percent = 0
            memory_used = memory_total = "N/A"
            uptime = "N/A"

        # Формируем итоговый словарь со всеми метриками
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
            "system": {
                "python_version": sys.version.split()[0],
                "os": platform.system(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used": memory_used,
                "memory_total": memory_total,
                "uptime": uptime,
            },
            "recent_orders": recent_orders,
            "recent_feedback": recent_feedback,
            "pending_reviews": pending_reviews,
            "recent_logs": recent_logs,
            "maintenance_mode": maintenance_mode,
            "cache_backend": cache_backend,
            "backup_count": backup_count,
        }

        # Кэшируем собранную статистику на 1 минуту, чтобы не пересчитывать при каждом обновлении админки
        cache.set(cache_key, stats, 60)

    # Имя переменной в шаблоне будет admin_stats
    return {"admin_stats": stats}


def statistics_banners(request):
    """
    Контекстный процессор для вывода статистических баннеров и счетчиков.
    Фильтрует баннеры в зависимости от страницы и типа пользователя.
    """
    from .models import StatisticsBanner
    
    # Определяем тип пользователя для ключа кэша
    user_type = 'user'
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user_type = 'admin'
        elif request.user.is_staff:
            user_type = 'staff'
            
    cache_key = f'statistics_banners_{user_type}'
    banners_by_position = cache.get(cache_key)
    
    if not banners_by_position:
        # Активные баннеры, отсортированные по порядку
        active_banners = StatisticsBanner.objects.filter(is_active=True).order_by('order')
        
        # Группируем баннеры по их позициям на странице (head, footer и т.д.)
        banners_by_position = {
            'head': [],
            'body_start': [],
            'body_end': [],
            'header': [],
            'footer': [],
            'custom': []
        }
        
        for banner in active_banners:
            # Проверяем права доступа к баннеру для текущего типа пользователя
            show_to_user = False
            if user_type == 'admin' and banner.enabled_for_admin:
                show_to_user = True
            elif user_type == 'staff' and banner.enabled_for_staff:
                show_to_user = True
            elif user_type == 'user' and banner.enabled_for_users:
                show_to_user = True
                
            if show_to_user:
                # Если доступ разрешен, добавляем отрендеренный код баннера
                rendered_code = banner.get_rendered_code(request)
                if rendered_code:
                    pos = banner.position
                    if pos in banners_by_position:
                        banners_by_position[pos].append(rendered_code)
        
        # Преобразуем списки кодов в готовые HTML-строки
        for pos in banners_by_position:
            banners_by_position[pos] = "\n".join(banners_by_position[pos])
        
        # Кэшируем результат на 15 минут
        cache.set(cache_key, banners_by_position, 900)
        
    return {'statistics_banners': banners_by_position}


def hero_overrides(request):
    """
    Контекстный процессор для получения настроек Hero-секции для крупных разделов сайта.
    Результат кэшируется на 5 минут по ключу, включающему path.
    """
    from .models import AppHeroSettings

    path = request.path

    # Определяем название раздела для поиска
    app_name = None
    if path == "/":
        app_name = "home"
    elif "/news/" in path:
        app_name = "news"
    elif "/portfolio/" in path:
        app_name = "portfolio"
    elif "/services/" in path:
        app_name = "services"
    elif "/knowledge_base/" in path:
        app_name = "knowledge_base"
    elif "/reviews/" in path:
        app_name = "reviews"
    elif "/contacts/" in path:
        app_name = "contacts"
    elif "/about/" in path:
        app_name = "about"
    elif "/profile/" in path:
        app_name = "profile"

    app_hero = None
    if app_name:
        cache_key = f"app_hero_{app_name}"
        app_hero = cache.get(cache_key)
        if app_hero is None:
            app_hero = AppHeroSettings.objects.filter(app_name=app_name).first()
            # Кэшируем даже None, чтобы не повторять запрос при отсутствии записи
            cache.set(cache_key, app_hero, 300)  # 5 минут

    return {
        "app_hero": app_hero,
        # Гарантируем наличие переменных для hero.html.
        # hero.html использует выражение вида: news|default:portfolio_item|default:service|...
        # В Django 5.x если переменная не существует в контексте — VariableDoesNotExist.
        # Если view уже передаёт эти переменные — context-processor НЕ переопределит их,
        # т.к. view-контекст имеет приоритет над context-processor в стеке Django.
        # Устанавливаем None только как значение по умолчанию (fallback).
        "portfolio_item": None,
        "service": None,
        "page": None,
        "news": None,
        "category": None,
        "page_title": None,
    }


def payment_methods(request):
    """
    Контекстный процессор для способов оплаты (мы принимаем).
    """
    from .models import PaymentMethod
    cache_key = "payment_methods_data"
    methods = cache.get(cache_key)

    if methods is None:
        methods = list(PaymentMethod.objects.filter(is_active=True).order_by("order", "name"))
        cache.set(cache_key, methods, 600)  # кэшируем на 10 минут

    return {"payment_methods": methods}
