# views.py
"""
ПРЕДСТАВЛЕНИЯ (КОНТРОЛЛЕРЫ) ДЛЯ ПРИЛОЖЕНИЯ MAIN

Этот файл содержит все представления (views) для публичной части приложения.
Представления обрабатывают HTTP-запросы и возвращают HTTP-ответы.

Основные классы:
1. MaintenanceMixin: Проверка статуса обслуживания сайта
2. BaseView: Базовый класс с общим контекстом
3. IndexView: Главная страница сайта
4. PageDetailView: Детальная страница контента
5. ProfileView: Страница профиля пользователя
6. ContactView, AboutView: Статические страницы
7. LogStatsView: Статистика лог-файлов

Все представления используют кэширование для оптимизации производительности.
"""

import re  # Модуль для работы с регулярными выражениями
from django.shortcuts import (
    render,
    reverse,
)  # | Функции для работы с запросами
from django.views.generic import (
    TemplateView,
    DetailView,
)  # | Базовые классы представлений
from django.utils.decorators import method_decorator  # | Декораторы для методов класса
from django.views.decorators.cache import cache_page  # | Декоратор кэширования страниц
from django.views.decorators.vary import (
    vary_on_cookie,
)  # | Декоратор для вариаций по кукам
from django.core.cache import cache  # | Система кэширования
from .models import SiteSettings, Page  # | Импорт моделей
from .breadcrumbs import get_breadcrumbs

# Импорт модели новостей (если приложение news установлено)
try:
    from news.models import News
except ImportError:
    News = None

# Импорт модели портфолио (если приложение portfolio установлено)
try:
    from portfolio.models import PortfolioItem
except ImportError:
    PortfolioItem = None


class MaintenanceMixin:
    """
    Миксин для проверки статуса обслуживания сайта.
    Перенаправляет на страницу закрытия, если сайт недоступен.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Перехватывает запрос и проверяет, не закрыт ли сайт.

        Действия:
        1. Загружает настройки сайта
        2. Проверяет флаг site_closed
        3. Если сайт закрыт и пользователь не персонал - показывает страницу закрытия

        Параметры:
            request: Объект HTTP-запроса
            *args, **kwargs: Дополнительные аргументы

        Возвращает:
            HttpResponse: Ответ с рендером страницы закрытия или продолжение обработки
        """
        site_settings = SiteSettings.load()

        if site_settings and site_settings.site_closed and not request.user.is_staff:
            # Для закрытого сайта показываем специальную страницу
            return render(
                request, 
                "main/site_closed.html", 
                {
                    "site_settings": site_settings
                }
            )

        return super().dispatch(request, *args, **kwargs)


class BaseView(TemplateView):
    """
    Базовый класс для всех представлений.
    Содержит общую логику для наследования.
    """

    def get_context_data(self, **kwargs):
        """
        Добавляет общие данные контекста для всех страниц.
        Включает настройки сайта и проверку статуса обслуживания.

        Действия:
        1. Получает настройки сайта с кэшированием
        2. Добавляет базовые SEO-данные
        3. Возвращает расширенный контекст

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста
        """
        context = super().get_context_data(**kwargs)

        # Получаем настройки сайта с кэшированием
        cache_key = "site_settings"
        site_settings = cache.get(cache_key)

        if not site_settings:
            site_settings = SiteSettings.load()
            if site_settings:
                cache.set(cache_key, site_settings, 300)  # | Кэш на 5 минут

        context["site_settings"] = site_settings

        # Добавляем базовые SEO данные
        context.setdefault(
            "page_title",
            getattr(site_settings, "logo_text", "DPITS-CMS.RU")
            if site_settings
            else "DPITS-CMS.RU",
        )
        context.setdefault(
            "meta_description",
            getattr(site_settings, "seo_description", "") if site_settings else "",
        )
        context.setdefault(
            "meta_keywords",
            getattr(site_settings, "seo_keywords", "") if site_settings else "",
        )

        return context


class ProfileView(MaintenanceMixin, BaseView):
    """
    Представление для страницы профиля пользователя.
    Отображает шаблон профиля с базовым контекстом.
    Требует аутентификации пользователя.
    """

    template_name = "main/profile.html"  # | Путь к шаблону

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет, аутентифицирован ли пользователь.

        Действия:
        1. Проверяет флаг is_authenticated
        2. Если не аутентифицирован - перенаправляет на страницу входа

        Параметры:
            request: Объект HTTP-запроса
            *args, **kwargs: Дополнительные аргументы

        Возвращает:
            HttpResponse: Перенаправление или продолжение обработки
        """
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            from django.shortcuts import resolve_url

            return redirect_to_login(
                request.get_full_path(), login_url=resolve_url("accounts:login")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Добавляет данные контекста для страницы профиля.

        Действия:
        1. Добавляет заголовок страницы
        2. Добавляет объект пользователя

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста профиля
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Профиль",
                "meta_description": "Профиль пользователя",
                "user": self.request.user,
                "breadcrumbs": get_breadcrumbs([
                    ("Профиль", reverse("accounts:profile"), "fas fa-user"),
                ]),
            }
        )
        return context


class IndexView(MaintenanceMixin, BaseView):
    """
    Представление для главной страницы сайта.
    Наследует функциональность обслуживания и базовые данные.
    """

    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        """
        Расширяет контекст данными для главной страницы.
        Включает рекомендуемые страницы и SEO-данные.

        Действия:
        1. Получает рекомендуемые страницы
        2. Получает последние новости
        3. Формирует SEO-заголовок и описание

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста главной страницы
        """
        context = super().get_context_data(**kwargs)
        site_settings = context.get("site_settings")

        # Получаем рекомендуемые страницы для главной
        cache_key = "featured_pages"
        featured_pages = cache.get(cache_key)

        if not featured_pages:
            featured_pages = list(
                Page.objects.filter(show_on_site=True).order_by("order", "title")[:6]
            )
            if featured_pages:
                cache.set(cache_key, featured_pages, 600)  # | Кэш на 10 минут

        # Получаем три последние новости
        recent_news_list = []
        if News:
            try:
                recent_news_list = list(
                    News.objects.filter(is_active=True).order_by("-created_at")[:3]
                )
            except Exception:
                # Если модель News не имеет поля is_active, используем другой фильтр
                try:
                    recent_news_list = list(
                        News.objects.all().order_by("-created_at")[:3]
                    )
                except Exception:
                    recent_news_list = []

        # SEO данные
        page_title = "Главная"
        if site_settings:
            if site_settings.seo_title:
                page_title = (
                    f"{site_settings.logo_text} - {site_settings.seo_title}"
                    if site_settings.logo_text
                    else site_settings.seo_title
                )
            elif site_settings.logo_text:
                page_title = site_settings.logo_text

        meta_description = ""
        if site_settings:
            if site_settings.short_description:
                # Убираем HTML теги и ограничиваем длину
                meta_description = re.sub(
                    r"<[^>]+>", "", str(site_settings.short_description)
                )
                meta_description = (
                    meta_description[:160]
                    if len(meta_description) > 160
                    else meta_description
                )
            elif site_settings.seo_description:
                meta_description = site_settings.seo_description

        # Получаем три последние работы из портфолио
        recent_portfolio_list = []
        if PortfolioItem:
            try:
                recent_portfolio_list = list(
                    PortfolioItem.objects.filter(status="published").order_by("-created_at")[:3]
                )
            except Exception:
                try:
                    recent_portfolio_list = list(
                        PortfolioItem.objects.all().order_by("-created_at")[:3]
                    )
                except Exception:
                    recent_portfolio_list = []

        context.update(
            {
                "featured_pages": featured_pages,
                "recent_news_list": recent_news_list,
                "recent_portfolio_list": recent_portfolio_list,
                "page_title": page_title,
                "meta_description": meta_description,
                # Эти переменные нужны для корректной работы hero.html
                "portfolio_item": None,
                "news": None,
                "service": None,
                "category": None,
                "page": None,
            }
        )

        return context

    @method_decorator(cache_page(60 * 15))  # | Кэшируем на 15 минут
    @method_decorator(vary_on_cookie)  # | Учитываем куки пользователя
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PageDetailView(MaintenanceMixin, DetailView):
    """
    Представление для отображения детальной информации о странице.
    """

    model = Page
    template_name = "main/page_detail.html"
    context_object_name = "page"  # | Имя объекта в контексте
    slug_field = "slug"  # | Поле для поиска по slug
    slug_url_kwarg = "slug"  # | Имя параметра в URL

    def get_queryset(self):
        """
        Возвращает только активные страницы (show_on_site=True).

        Возвращает:
            QuerySet: Фильтрованный QuerySet активных страниц
        """
        return Page.objects.filter(show_on_site=True)

    def get_context_data(self, **kwargs):
        """
        Добавляет SEO-данные и связанный контент.

        Действия:
        1. Получает предыдущую и следующую страницы
        2. Формирует SEO-заголовок и описание
        3. Добавляет ключевые слова

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста страницы
        """
        context = super().get_context_data(**kwargs)
        page = self.object
        site_settings = SiteSettings.load()

        # Получаем предыдущую и следующую страницы
        prev_page = page.get_previous_page()
        next_page = page.get_next_page()

        # SEO-данные страницы
        page_title = page.display_title
        if site_settings and site_settings.logo_text:
            page_title = f"{page.display_title} - {site_settings.logo_text}"

        # Мета-описание
        meta_description = page.seo_description
        if not meta_description and page.content:
            meta_description = re.sub(r"<[^>]+>", "", str(page.content))
            meta_description = (
                meta_description[:160]
                if len(meta_description) > 160
                else meta_description
            )

        context.update(
            {
                "site_settings": site_settings,
                "page_title": page_title,
                "meta_description": meta_description,
                "meta_keywords": page.seo_keywords,
                "prev_page": prev_page,
                "next_page": next_page,
                "breadcrumbs": get_breadcrumbs([
                    (page.title, page.get_absolute_url()),
                ]),
            }
        )

        return context

    @method_decorator(cache_page(60 * 10))  # | Кэшируем на 10 минут
    @method_decorator(vary_on_cookie)  # | Учитываем куки пользователя
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ContactView(MaintenanceMixin, TemplateView):
    """
    Представление для страницы контактов.
    """

    template_name = "main/contacts.html"

    def get_context_data(self, **kwargs):
        """
        Добавляет контекст для страницы контактов.

        Действия:
        1. Формирует заголовок страницы
        2. Добавляет описание

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста контактов
        """
        context = super().get_context_data(**kwargs)
        site_settings = SiteSettings.load()

        page_title = "Контакты"
        if site_settings and site_settings.logo_text:
            page_title = f"Контакты - {site_settings.logo_text}"

        meta_description = "Контактная информация и способы связи"
        if site_settings and site_settings.seo_description:
            meta_description = site_settings.seo_description

        context.update(
            {
                "site_settings": site_settings,
                "page_title": page_title,
                "meta_description": meta_description,
                "breadcrumbs": get_breadcrumbs([
                    ("Контакты", reverse("main:contacts"), "fas fa-phone"),
                ]),
            }
        )
        return context


class AboutView(MaintenanceMixin, TemplateView):
    """
    Представление для страницы "О нас".
    """

    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        """
        Добавляет контекст для страницы "О нас".

        Действия:
        1. Формирует заголовок страницы
        2. Создает описание из краткого описания сайта

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста "О нас"
        """
        context = super().get_context_data(**kwargs)
        site_settings = SiteSettings.load()

        page_title = "О нас"
        if site_settings and site_settings.logo_text:
            page_title = f"О нас - {site_settings.logo_text}"

        meta_description = "Информация о нашей компании и услугах"
        if site_settings:
            if site_settings.short_description:
                meta_description = re.sub(
                    r"<[^>]+>", "", str(site_settings.short_description)
                )
                meta_description = (
                    meta_description[:160]
                    if len(meta_description) > 160
                    else meta_description
                )
            elif site_settings.seo_description:
                meta_description = site_settings.seo_description

        context.update(
            {
                "site_settings": site_settings,
                "page_title": page_title,
                "meta_description": meta_description,
                "breadcrumbs": get_breadcrumbs([
                    ("О нас", reverse("main:about"), "fas fa-info-circle"),
                ]),
            }
        )
        return context


def custom_404_view(request, exception):
    """
    Кастомная страница 404 ошибки.

    Действия:
    1. Создает контекст с настройками сайта
    2. Рендерит шаблон 404.html
    3. Возвращает ответ с кодом 404

    Параметры:
        request: Объект HTTP-запроса
        exception: Исключение, вызвавшее ошибку 404

    Возвращает:
        HttpResponse: Ответ с рендером страницы 404
    """
    site_settings = SiteSettings.load()
    context = {
        "site_settings": site_settings,
        "exception": exception,
        "page_title": "Страница не найдена (404)",
        "meta_description": "Запрашиваемая страница не найдена",
        "breadcrumbs": get_breadcrumbs([
            ("404 Error", None, "fas fa-exclamation-circle"),
        ]),
    }
    return render(
        request,
        "main/404.html",
        context,
        status=404,  # | Указываем код статуса 404
    )


def custom_500_view(request):
    """
    Кастомная страница 500 ошибки.

    Действия:
    1. Создает контекст с настройками сайта
    2. Рендерит шаблон 500.html
    3. Возвращает ответ с кодом 500

    Параметры:
        request: Объект HTTP-запроса

    Возвращает:
        HttpResponse: Ответ с рендером страницы 500
    """
    site_settings = SiteSettings.load()
    context = {
        "site_settings": site_settings,
        "page_title": "Ошибка сервера (500)",
        "meta_description": "Произошла внутренняя ошибка сервера",
        "breadcrumbs": get_breadcrumbs([
            ("500 Error", None, "fas fa-bug"),
        ]),
    }
    return render(
        request,
        "main/500.html",
        context,
        status=500,  # | Указываем код статуса 500
    )


class LogStatsView(MaintenanceMixin, BaseView):
    """
    Представление для отображения статистики лог-файлов.
    Показывает информацию о debug.log и позволяет управлять им.

    Доступно только для администраторов и персонала.
    """

    template_name = "main/log_stats.html"  # | Шаблон для отображения статистики

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет права доступа пользователя.
        Доступ только для администраторов и персонала.

        Действия:
        1. Проверяет is_authenticated и is_staff
        2. Если нет прав - перенаправляет на страницу входа

        Параметры:
            request: Объект HTTP-запроса
            *args, **kwargs: Дополнительные аргументы

        Возвращает:
            HttpResponse: Перенаправление или продолжение обработки
        """
        if not request.user.is_authenticated or not request.user.is_staff:
            from django.contrib.auth.views import redirect_to_login
            from django.shortcuts import resolve_url

            return redirect_to_login(
                request.get_full_path(), login_url=resolve_url("accounts:login")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Добавляет данные о лог-файле в контекст.

        Действия:
        1. Получает информацию о лог-файле (размер, количество строк, категории)
        2. Получает последние строки лога для предпросмотра
        3. Формирует SEO-данные для страницы
        4. Добавляет статистику по категориям

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста статистики логов
        """
        context = super().get_context_data(**kwargs)

        # Импортируем функции для работы с лог-файлом
        from .log_utils import (
            get_log_file_info,      # Получение полной информации о файле
            get_recent_log_lines,   # Получение последних строк
            count_total_lines,      # Подсчет общего количества строк
            count_lines_by_category # Подсчет строк по категориям
        )

        # Получаем полную информацию о лог-файле
        # Включает: размер, путь, количество строк, категории, дату изменения
        log_info = get_log_file_info()

        # Получаем последние 50 строк лога для отображения на странице
        recent_lines = get_recent_log_lines(50)

        # Дополнительно получаем статистику напрямую (на случай если нужна точность)
        total_lines = count_total_lines()  # Общее количество строк в файле
        categories = count_lines_by_category()  # Словарь с количеством по категориям

        # Формируем SEO-заголовок страницы
        page_title = "Статистика логов"
        site_settings = context.get("site_settings")
        if site_settings and site_settings.logo_text:
            # Если есть настройки сайта, добавляем название сайта к заголовку
            page_title = f"Статистика логов - {site_settings.logo_text}"

        # Обновляем контекст шаблона данными для отображения
        context.update(
            {
                "log_info": log_info,              # Полная информация о лог-файле
                "recent_lines": recent_lines,      # Последние строки лога для предпросмотра
                "total_lines": total_lines,        # Общее количество строк (для удобства)
                "categories": categories,          # Счетчики по категориям (для удобства)
                "page_title": page_title,          # Заголовок страницы для <title>
                "meta_description": "Статистика и управление лог-файлами системы. Просмотр количества строк, анализ по категориям (ERROR, WARNING, INFO, DEBUG), очистка логов.",
                "breadcrumbs": get_breadcrumbs([
                    ("Статистика логов", reverse("main:log_stats"), "fas fa-list-alt"),
                ]),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы для управления логами.
        Поддерживает очистку лог-файла.

        Действия:
        1. Получает действие из POST-данных
        2. Если action == "clear_log" - очищает лог-файл
        3. Добавляет сообщение об успехе/ошибке
        4. Возвращает ответ GET

        Параметры:
            request: Объект HTTP-запроса
            *args, **kwargs: Дополнительные аргументы

        Возвращает:
            HttpResponse: Ответ с рендером страницы статистики
        """
        from .log_utils import clear_log_file
        from django.contrib import messages

        action = request.POST.get("action")  # | Получаем тип действия

        if action == "clear_log":
            success, message = clear_log_file()  # | Очищаем лог-файл
            if success:
                messages.success(request, message)  # | Сообщение об успехе
            else:
                messages.error(request, message)  # | Сообщение об ошибке

        return self.get(request, *args, **kwargs)  # | Возвращаем GET-ответ


class ErrorLogView(MaintenanceMixin, BaseView):
    """
    Представление для отображения лог-файла ошибок (error.log).
    Показывает информацию об error.log и позволяет управлять им.

    Доступно только для суперпользователей (is_superuser).
    """

    template_name = "main/error_log.html"  # | Шаблон для отображения ошибок

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет права доступа пользователя.
        Доступ только для суперпользователей.

        Действия:
        1. Проверяет is_authenticated и is_superuser
        2. Если нет прав - перенаправляет на страницу входа

        Параметры:
            request: Объект HTTP-запроса
            *args, **kwargs: Дополнительные аргументы

        Возвращает:
            HttpResponse: Перенаправление или продолжение обработки
        """
        if not request.user.is_authenticated or not request.user.is_superuser:
            from django.contrib.auth.views import redirect_to_login
            from django.shortcuts import resolve_url

            return redirect_to_login(
                request.get_full_path(), login_url=resolve_url("accounts:login")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Добавляет данные о error.log в контекст.

        Действия:
        1. Получает информацию о error.log (размер, количество строк, категории)
        2. Получает последние строки лога для предпросмотра
        3. Формирует SEO-данные для страницы
        4. Добавляет статистику по категориям

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста лога ошибок
        """
        context = super().get_context_data(**kwargs)

        # Импортируем функции для работы с error.log
        from .log_utils import (
            get_error_log_file_info,      # Получение полной информации о файле
            get_error_log_recent_lines,   # Получение последних строк
            count_total_lines,            # Подсчет общего количества строк
            count_lines_by_category       # Подсчет строк по категориям
        )

        # Получаем полную информацию о error.log
        # Включает: размер, путь, количество строк, категории, дату изменения
        log_info = get_error_log_file_info()

        # Получаем последние 100 строк лога для отображения на странице
        recent_lines = get_error_log_recent_lines(100)

        # Дополнительно получаем статистику напрямую
        if log_info.get('file_path'):
            total_lines = count_total_lines(log_info['file_path'])
            categories = count_lines_by_category(log_info['file_path'])
        else:
            total_lines = 0
            categories = {
                'ERROR': 0,
                'WARNING': 0,
                'INFO': 0,
                'DEBUG': 0,
                'OTHER': 0
            }

        # Формируем SEO-заголовок страницы
        page_title = "Лог ошибок"
        site_settings = context.get("site_settings")
        if site_settings and site_settings.logo_text:
            # Если есть настройки сайта, добавляем название сайта к заголовку
            page_title = f"Лог ошибок - {site_settings.logo_text}"

        # Обновляем контекст шаблона данными для отображения
        context.update(
            {
                "log_info": log_info,              # Полная информация о error.log
                "recent_lines": recent_lines,      # Последние строки лога для предпросмотра
                "total_lines": total_lines,        # Общее количество строк (для удобства)
                "categories": categories,          # Счетчики по категориям (для удобства)
                "page_title": page_title,          # Заголовок страницы для <title>
                "meta_description": "Просмотр и управление лог-файлом ошибок системы. Статистика по категориям (ERROR, WARNING, INFO, DEBUG), очистка логов.",
                "breadcrumbs": get_breadcrumbs([
                    ("Лог ошибок", reverse("main:error_log"), "fas fa-exclamation-triangle"),
                ]),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы для управления error.log.
        Поддерживает очистку лог-файла с подтверждением.

        Действия:
        1. Получает действие из POST-данных
        2. Если action == "clear_log" - очищает error.log
        3. Добавляет сообщение об успехе/ошибке
        4. Возвращает ответ GET

        Параметры:
            request: Объект HTTP-запроса
            *args, **kwargs: Дополнительные аргументы

        Возвращает:
            HttpResponse: Ответ с рендером страницы лога ошибок
        """
        from .log_utils import clear_error_log_file
        from django.contrib import messages

        action = request.POST.get("action")  # | Получаем тип действия

        if action == "clear_log":
            success, message = clear_error_log_file()  # | Очищаем error.log
            if success:
                messages.success(request, message)  # | Сообщение об успехе
            else:
                messages.error(request, message)  # | Сообщение об ошибке

        return self.get(request, *args, **kwargs)  # | Возвращаем GET-ответ
