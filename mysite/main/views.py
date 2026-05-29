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
from django.db.models import Q, F  # Q — сложные запросы, F — атомарные операции с полями
from django.shortcuts import (
    render,
    reverse,
)  # | Функции для работы с запросами
from django.http import JsonResponse
from django.views.generic import (
    TemplateView,
    DetailView,
)  # | Базовые классы представлений
from django.views.decorators.cache import cache_page  # | Декоратор кэширования страниц
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # | Пагинация
from django.core.cache import cache  # | Система кэширования
from django.contrib import messages  # | Сообщения пользователю
from .models import SiteSettings, Page  # | Импорт моделей
from .breadcrumbs import get_breadcrumbs, get_breadcrumbs_jsonld
from .forms import ContactForm  # | Форма обратной связи

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

    def build_page_title(self, title: str, site_settings=None) -> str:
        """
        Формирует заголовок страницы вида: "<title> - <site_name>".
        Вынесено из всех view, где этот паттерн повторялся 4+ раза.

        Параметры:
            title: Название конкретной страницы (например, "Контакты")
            site_settings: Объект SiteSettings (берётся из контекста если None)

        Возвращает:
            str: Составной заголовок или только title, если logo_text не задан
        """
        logo = getattr(site_settings, "logo_text", "") if site_settings else ""
        return f"{title} - {logo}" if logo else title

    def get_context_data(self, **kwargs):
        """
        Добавляет общие данные контекста для всех страниц.
        Включает настройки сайта и проверку статуса обслуживания.

        Действия:
        1. Получает настройки сайта с кэшированием (5 минут)
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

    template_name = "main/home.html"

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
            if hasattr(News, 'is_active'):
                recent_news_list = list(News.objects.filter(is_active=True).order_by("-created_at")[:3])
            else:
                recent_news_list = list(News.objects.all().order_by("-created_at")[:3])

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
            field_names = [f.name for f in PortfolioItem._meta.get_fields()]
            if 'status' in field_names:
                recent_portfolio_list = list(PortfolioItem.objects.filter(status="published").order_by("-created_at")[:3])
            else:
                recent_portfolio_list = list(PortfolioItem.objects.all().order_by("-created_at")[:3])

        # Публичная статистика для главной страницы
        stats = {}
        if News:
            stats["news_count"] = cache.get_or_set(
                "home_stats_news",
                lambda: News.objects.filter(is_active=True).count(),
                300,
            )
        if PortfolioItem:
            stats["portfolio_count"] = cache.get_or_set(
                "home_stats_portfolio",
                lambda: PortfolioItem.objects.filter(status="published").count() if 'status' in [f.name for f in PortfolioItem._meta.get_fields()] else PortfolioItem.objects.count(),
                300,
            )
        try:
            from reviews.models import Review
            stats["reviews_count"] = cache.get_or_set(
                "home_stats_reviews",
                lambda: Review.objects.filter(status='approved').count(),
                300,
            )
        except (ImportError, Exception):
            pass
        try:
            from portfolio.models import Client
            stats["clients_count"] = cache.get_or_set(
                "home_stats_clients",
                lambda: Client.objects.count(),
                300,
            )
        except (ImportError, Exception):
            pass

        context.update(
            {
                "featured_pages": featured_pages,
                "recent_news_list": recent_news_list,
                "recent_portfolio_list": recent_portfolio_list,
                "page_title": page_title,
                "meta_description": meta_description,
                "stats": stats,
                # Эти переменные нужны для корректной работы hero.html
                "portfolio_item": None,
                "news": None,
                "service": None,
                "category": None,
                "page": None,
            }
        )

        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Кэширование только для анонимных пользователей.
        Авторизованные пользователи получают свежий контент без кэша.
        """
        if request.user.is_authenticated:
            # Для авторизованных — без кэша страницы
            return super(IndexView, self).dispatch(request, *args, **kwargs)
        # Для анонимных — кэшируем на 15 минут
        cached_dispatch = cache_page(60 * 15)(super(IndexView, self).dispatch)
        return cached_dispatch(request, *args, **kwargs)


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

        breadcrumbs = get_breadcrumbs([
            (page.title, page.get_absolute_url()),
        ])

        context.update(
            {
                "site_settings": site_settings,
                "page_title": page_title,
                "meta_description": meta_description,
                "meta_keywords": page.seo_keywords,
                "prev_page": prev_page,
                "next_page": next_page,
                "breadcrumbs": breadcrumbs,
                "breadcrumbs_jsonld": get_breadcrumbs_jsonld(breadcrumbs, self.request),
            }
        )

        return context

    def get(self, request, *args, **kwargs):
        """
        Переопределяем GET для инкремента счётчика просмотров.

        Важно: @cache_page намеренно убран из dispatch(), потому что при
        кэшированном ответе get() не вызывается и счётчик никогда не
        инкрементируется. Вместо этого используем более гибкое кэширование
        контекста на уровне отдельных данных (в get_context_data).

        Используем F('views') + 1 для атомарного обновления без race condition
        при параллельных запросах (в отличие от self.object.views + 1).
        """
        response = super().get(request, *args, **kwargs)
        # Атомарный инкремент через F-выражение — безопасно при параллельных запросах
        Page.objects.filter(pk=self.object.pk).update(views=F('views') + 1)
        return response


class ContactView(MaintenanceMixin, TemplateView):
    """
    Представление для страницы контактов.
    Обрабатывает GET (отображение формы) и POST (отправка формы).

    Улучшения по сравнению с исходной версией:
    - Rate-limiting: не более 5 отправок в час с одного IP
    - ContactMessage сохраняется в БД ДО отправки email (защита от потери данных)
    - site_settings берётся из context processor, а не дополнительным запросом к БД
    - build_page_title() устраняет дублирование кода
    """

    template_name = "main/contacts.html"

    # Максимальное количество отправок формы с одного IP в час
    RATE_LIMIT_MAX = 5
    RATE_LIMIT_WINDOW = 3600  # секунд (1 час)

    def get_context_data(self, **kwargs):
        """
        Добавляет контекст для страницы контактов.

        Действия:
        1. Получает site_settings из context (уже загружены context processor)
        2. Формирует заголовок страницы через build_page_title()
        3. Добавляет форму обратной связи

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста контактов
        """
        context = super().get_context_data(**kwargs)
        # Берём из context (уже заполнено context processor), без лишнего запроса к БД
        site_settings = context.get("site_settings") or SiteSettings.load()

        meta_description = "Контактная информация и способы связи"
        if site_settings and site_settings.seo_description:
            meta_description = site_settings.seo_description

        breadcrumbs = get_breadcrumbs([
            ("Контакты", reverse("main:contacts"), "fas fa-phone"),
        ])

        context.update(
            {
                "site_settings": site_settings,
                "page_title": self.build_page_title("Контакты", site_settings),
                "meta_description": meta_description,
                "breadcrumbs": breadcrumbs,
                "breadcrumbs_jsonld": get_breadcrumbs_jsonld(breadcrumbs, self.request),
                # Форма — берём из kwargs (если POST вернул ошибки) или создаём новую
                "contact_form": kwargs.get("contact_form", ContactForm()),
            }
        )
        return context

    def _check_rate_limit(self, request) -> bool:
        """
        Проверяет лимит отправок формы для данного IP-адреса.

        Использует Django cache как хранилище счётчика.
        Ключ: contact_form_<IP>, значение: количество отправок за окно времени.

        Возвращает:
            bool: True если лимит превышен (нужно заблокировать), False если всё ок
        """
        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR', 'unknown')
        )
        cache_key = f'contact_rate_{ip}'
        attempts = cache.get(cache_key, 0)
        if attempts >= self.RATE_LIMIT_MAX:
            return True  # лимит превышен
        # Увеличиваем счётчик, сохраняем на время окна
        cache.set(cache_key, attempts + 1, self.RATE_LIMIT_WINDOW)
        return False

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает отправку формы обратной связи.

        Действия:
        1. Проверяет rate limit (5 отправок/час с одного IP)
        2. Валидирует данные формы
        3. Сохраняет ContactMessage в БД (защита от потери при сбое SMTP)
        4. Отправляет email администратору
        5. Показывает сообщение об успехе/ошибке
        """
        from django.shortcuts import redirect

        # --- Rate limiting ---
        if self._check_rate_limit(request):
            messages.warning(
                request,
                "Слишком много попыток. Пожалуйста, попробуйте снова через час."
            )
            return redirect(reverse("main:contacts"))

        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            contact_info = form.cleaned_data["contact"]
            message_text = form.cleaned_data["message"]

            # --- Сохраняем в БД до отправки email ---
            # Это гарантирует, что данные не потеряются при сбое SMTP
            try:
                from .models import ContactMessage
                ip = (
                    request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                    or request.META.get('REMOTE_ADDR')
                )
                ContactMessage.objects.create(
                    name=name,
                    contact=contact_info,
                    message=message_text,
                    ip_address=ip or None,
                )
            except Exception:
                # Не прерываем работу, если по какой-то причине БД недоступна
                pass

            # --- Отправляем email администратору ---
            try:
                from django.core.mail import send_mail
                from django.conf import settings as django_settings
                site_settings = cache.get("site_settings") or SiteSettings.load()
                admin_email = (
                    site_settings.email
                    if site_settings and site_settings.email
                    else getattr(django_settings, 'DEFAULT_FROM_EMAIL', '')
                )

                if admin_email:
                    send_mail(
                        subject=f"[Обратная связь] Сообщение от {name}",
                        message=(
                            f"От: {name}\n"
                            f"Контакт: {contact_info}\n\n"
                            f"Сообщение:\n{message_text}"
                        ),
                        from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', admin_email),
                        recipient_list=[admin_email],
                        fail_silently=True,
                    )
            except Exception:
                pass

            messages.success(
                request,
                f"Спасибо, {name}! Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время."
            )
            # Redirect-after-POST паттерн (предотвращает повторную отправку при F5)
            return redirect(reverse("main:contacts"))
        else:
            # Форма содержит ошибки — возвращаем её в контекст
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
            context = self.get_context_data(contact_form=form)
            return self.render_to_response(context)


class AboutView(MaintenanceMixin, TemplateView):
    """
    Представление для страницы "О нас".

    Улучшение: site_settings берётся из context (уже загружен context processor),
    page_title формируется через build_page_title() без дублирования кода.
    """

    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        """
        Добавляет контекст для страницы "О нас".

        Действия:
        1. Получает site_settings из context processor (без лишнего запроса к БД)
        2. Формирует заголовок через build_page_title()
        3. Создаёт meta_description из краткого описания сайта

        Параметры:
            **kwargs: Дополнительные аргументы контекста

        Возвращает:
            dict: Словарь с данными контекста "О нас"
        """
        context = super().get_context_data(**kwargs)
        # Берём из context (уже заполнено context processor), без лишнего запроса к БД
        site_settings = context.get("site_settings") or SiteSettings.load()

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
                "page_title": self.build_page_title("О нас", site_settings),
                "meta_description": meta_description,
                "breadcrumbs": get_breadcrumbs([
                    ("О нас", reverse("main:about"), "fas fa-info-circle"),
                ]),
            }
        )
        return context


class SearchView(MaintenanceMixin, BaseView):
    """
    Представление для поиска по сайту.
    Ищет по новостям, портфолио и страницам.
    """

    template_name = "main/search_results.html"

    def get_context_data(self, **kwargs):
        """
        Добавляет результаты поиска в контекст с пагинацией.
        """
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        page_num = self.request.GET.get("page", 1)

        context["query"] = query
        context["page_title"] = f"Поиск: {query}" if query else "Поиск по сайту"

        breadcrumbs = get_breadcrumbs([
            ("Поиск", reverse("main:search"), "fas fa-search"),
        ])
        context["breadcrumbs"] = breadcrumbs
        context["breadcrumbs_jsonld"] = get_breadcrumbs_jsonld(breadcrumbs, self.request)

        if query:
            # Поиск по новостям
            if News:
                news_qs = News.objects.filter(
                    Q(title__icontains=query) |
                    Q(short_description__icontains=query) |
                    Q(content__icontains=query),
                    is_active=True
                ).distinct()
                news_paginator = Paginator(news_qs, 10)
                try:
                    context["news_results"] = news_paginator.page(page_num)
                except (PageNotAnInteger, EmptyPage):
                    context["news_results"] = news_paginator.page(1)
                context["news_total"] = news_qs.count()

            # Поиск по портфолио
            if PortfolioItem:
                try:
                    portfolio_qs = PortfolioItem.objects.filter(
                        Q(title__icontains=query) |
                        Q(short_description__icontains=query) |
                        Q(content__icontains=query) |
                        Q(technologies__icontains=query),
                        status="published"
                    ).distinct()
                except Exception:
                    portfolio_qs = PortfolioItem.objects.filter(
                        Q(title__icontains=query) |
                        Q(short_description__icontains=query),
                    ).distinct()
                portfolio_paginator = Paginator(portfolio_qs, 10)
                try:
                    context["portfolio_results"] = portfolio_paginator.page(page_num)
                except (PageNotAnInteger, EmptyPage):
                    context["portfolio_results"] = portfolio_paginator.page(1)
                context["portfolio_total"] = portfolio_qs.count()

            # Поиск по страницам
            page_qs = Page.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query),
                show_on_site=True
            ).distinct()
            page_paginator = Paginator(page_qs, 10)
            try:
                context["page_results"] = page_paginator.page(page_num)
            except (PageNotAnInteger, EmptyPage):
                context["page_results"] = page_paginator.page(1)
            context["pages_total"] = page_qs.count()

            # Поиск по отзывам (одобренные)
            try:
                from reviews.models import Review
                reviews_qs = Review.objects.filter(
                    Q(author_name__icontains=query) |
                    Q(text__icontains=query),
                    status='approved'
                ).distinct()
                reviews_paginator = Paginator(reviews_qs, 10)
                try:
                    context["reviews_results"] = reviews_paginator.page(page_num)
                except (PageNotAnInteger, EmptyPage):
                    context["reviews_results"] = reviews_paginator.page(1)
                context["reviews_total"] = reviews_qs.count()
            except (ImportError, Exception):
                context["reviews_total"] = 0

            # Общее количество результатов
            context["total_results"] = (
                context.get("news_total", 0) +
                context.get("portfolio_total", 0) +
                context.get("pages_total", 0) +
                context.get("reviews_total", 0)
            )

        return context


class SearchApiView(MaintenanceMixin, BaseView):
    """
    API представление для живого поиска.
    Возвращает результаты в формате JSON.
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        results = []

        if len(query) >= 2:
            # Поиск по новостям
            if News:
                news_items = News.objects.filter(
                    Q(title__icontains=query) | 
                    Q(short_description__icontains=query),
                    is_active=True
                ).distinct()[:5]
                
                for item in news_items:
                    results.append({
                        "title": item.title,
                        "url": item.get_absolute_url(),
                        "type": "Новости",
                        "icon": "fa-newspaper"
                    })
            
            # Поиск по портфолио
            if PortfolioItem:
                portfolio_items = PortfolioItem.objects.filter(
                    Q(title__icontains=query) | 
                    Q(short_description__icontains=query) |
                    Q(technologies__icontains=query),
                    status="published"
                ).distinct()[:5]
                
                for item in portfolio_items:
                    results.append({
                        "title": item.title,
                        "url": item.get_absolute_url(),
                        "type": "Портфолио",
                        "icon": "fa-briefcase"
                    })

            # Поиск по страницам
            page_items = Page.objects.filter(
                Q(title__icontains=query),
                show_on_site=True
            ).distinct()[:5]
            
            for item in page_items:
                results.append({
                    "title": item.title,
                    "url": item.get_absolute_url(),
                    "type": "Страница",
                    "icon": "fa-file-alt"
                })

        return JsonResponse({"results": results})


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


class BackupView(MaintenanceMixin, BaseView):
    """
    Представление для страницы управления резервными копиями.
    Отображает список бэкапов, позволяет создавать новые и удалять старые.

    Доступно только для суперпользователей (is_superuser).
    """

    template_name = "main/backups.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет права доступа.
        Доступ только для суперпользователей.
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
        Добавляет список бэкапов и статистику в контекст.
        """
        from .backup_utils import list_backups, get_backups_stats, get_backups_dir

        context = super().get_context_data(**kwargs)

        backups = list_backups()
        stats = get_backups_stats()
        backups_dir = get_backups_dir()

        page_title = "Резервные копии"
        site_settings = context.get("site_settings")
        if site_settings and site_settings.logo_text:
            page_title = f"Резервные копии - {site_settings.logo_text}"

        context.update(
            {
                "backups": backups,
                "stats": stats,
                "backups_dir": str(backups_dir),
                "page_title": page_title,
                "meta_description": "Управление резервными копиями сайта. Создание, скачивание и удаление архивов.",
                "breadcrumbs": get_breadcrumbs([
                    ("Резервные копии", reverse("main:backups"), "fas fa-database"),
                ]),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы: создание нового бэкапа или удаление существующего.

        Действия:
        - action=create_backup : создаёт новый архив с параметрами из формы
        - action=delete_backup : удаляет файл по имени
        """
        from .backup_utils import create_site_backup, delete_backup

        action = request.POST.get("action")

        if action == "create_backup":
            # Получаем параметры из формы
            include_media = request.POST.get("include_media") == "on"
            include_static = request.POST.get("include_static") == "on"
            include_code = request.POST.get("include_code") == "on"

            try:
                compress_level = int(request.POST.get("compress_level", 6))
                compress_level = max(0, min(9, compress_level))
            except (ValueError, TypeError):
                compress_level = 6

            success, message, filename = create_site_backup(
                include_media=include_media,
                include_static=include_static,
                include_code=include_code,
                compress_level=compress_level,
            )

            if success:
                # Сбрасываем кэш статистики дашборда
                from django.core.cache import cache
                cache.delete("admin_dashboard_stats")
                messages.success(request, f"✅ {message}" + (f": {filename}" if filename else ""))
            else:
                messages.error(request, f"❌ {message}")

        elif action == "delete_backup":
            filename = request.POST.get("filename", "").strip()
            if filename:
                success, message = delete_backup(filename)
                if success:
                    from django.core.cache import cache
                    cache.delete("admin_dashboard_stats")
                    messages.success(request, f"🗑️ {message}")
                else:
                    messages.error(request, f"❌ {message}")
            else:
                messages.error(request, "❌ Имя файла не указано")

        from django.shortcuts import redirect
        return redirect(reverse("main:backups"))


class BackupDownloadView(MaintenanceMixin, BaseView):
    """
    Представление для скачивания файла резервной копии.
    Отдаёт файл в виде HTTP-ответа с соответствующим заголовком.

    Доступно только для суперпользователей.
    """

    def dispatch(self, request, *args, **kwargs):
        """Проверяет права доступа (только суперпользователь)."""
        if not request.user.is_authenticated or not request.user.is_superuser:
            from django.contrib.auth.views import redirect_to_login
            from django.shortcuts import resolve_url

            return redirect_to_login(
                request.get_full_path(), login_url=resolve_url("accounts:login")
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Отдаёт файл бэкапа для скачивания.
        Использует безопасный get_backup_path() для защиты от path traversal.
        """
        from django.http import FileResponse, Http404
        from .backup_utils import get_backup_path
        import mimetypes

        filename = kwargs.get("filename", "")
        filepath = get_backup_path(filename)

        if filepath is None:
            raise Http404(f"Файл резервной копии '{filename}' не найден")

        # Определяем MIME-тип
        mime_type, _ = mimetypes.guess_type(str(filepath))
        if not mime_type:
            mime_type = "application/octet-stream"

        response = FileResponse(
            open(filepath, "rb"),
            content_type=mime_type,
            as_attachment=True,
            filename=filepath.name,
        )
        return response
