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

    if not settings:
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


def sidebar_data(request):
    """
    Контекстный процессор для данных сайдбара (боковой панели).
    Собирает последние новости, работы портфолио и отзывы.
    """
    cache_key = "sidebar_data"
    sidebar_data = cache.get(cache_key)

    if not sidebar_data:
        sidebar_data = {}
        # Динамический импорт моделей других приложений
        # Используется try-except, чтобы сайт не падал, если какое-то приложение не установлено
        try:
            from news.models import News
            # Получаем 3 последние активные новости
            sidebar_data["sidebar_news"] = list(
                News.objects.filter(is_active=True).order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_news"] = []

        try:
            from portfolio.models import PortfolioItem
            # Получаем 3 последние завершенные работы
            sidebar_data["sidebar_portfolio"] = list(
                PortfolioItem.objects.all().order_by("-created_at")[:3]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_portfolio"] = []

        try:
            from reviews.models import Review
            # Получаем 2 последних одобренных отзыва
            # ИСПРАВЛЕНО: использование status='approved' вместо is_approved=True
            sidebar_data["sidebar_reviews"] = list(
                Review.objects.filter(status='approved').order_by("-created_at")[:2]
            )
        except (ImportError, AttributeError):
            sidebar_data["sidebar_reviews"] = []

        # Кэшируем собранные данные на 10 минут
        cache.set(cache_key, sidebar_data, 600)
    
    return sidebar_data


def seo_context(request):
    """
    Добавляет базовую SEO-информацию из глобальных настроек сайта.
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
            new_feedback = FeedbackMessage.objects.filter(is_read=False).count()
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

        # 7. Информация о логах приложений
        from .log_utils import get_log_file_info, get_error_log_file_info
        
        # Получаем данные о debug.log
        debug_log_info = get_log_file_info()
        # Получаем данные о error.log
        error_log_info = get_error_log_file_info()

        # Получаем последнюю запись статистики из БД
        last_log_stats = LogStats.objects.first()

        # 8. Системные характеристики сервера (CPU, Память, Версии)
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
            }
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
    Также инициализирует переменные, используемые в hero.html, чтобы избежать ошибок VariableDoesNotExist.
    """
    from .models import AppHeroSettings

    app_hero = None
    path = request.path

    if path == "/":
        app_hero = AppHeroSettings.objects.filter(app_name="home").first()
    elif "/news/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="news").first()
    elif "/portfolio/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="portfolio").first()
    elif "/services/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="services").first()
    elif "/reviews/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="reviews").first()
    elif "/contacts/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="contacts").first()
    elif "/about/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="about").first()
    elif "/profile/" in path:
        app_hero = AppHeroSettings.objects.filter(app_name="profile").first()

    return {
        "app_hero": app_hero,
        # Инициализируем переменные для hero.html как None
        "news": None,
        "portfolio_item": None,
        "service": None,
        "category": None,
        "page": None,
    }

