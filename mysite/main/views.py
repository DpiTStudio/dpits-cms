# views.py
# Представления (контроллеры) для приложения main
import re
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.http import Http404
from django.db.models import Q
from .models import SiteSettings, Page

# Импорт модели новостей (если приложение news установлено)
try:
    from news.models import News
except ImportError:
    News = None


class MaintenanceMixin:
    """
    Миксин для проверки статуса обслуживания сайта.
    Перенаправляет на страницу закрытия, если сайт недоступен.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Перехватывает запрос и проверяет, не закрыт ли сайт.
        """
        site_settings = SiteSettings.load()

        if site_settings and site_settings.site_closed and not request.user.is_staff:
            # Для закрытого сайта показываем специальную страницу
            return render(
                request, "main/site_closed.html", {"site_settings": site_settings}
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
        """
        context = super().get_context_data(**kwargs)

        # Получаем настройки сайта с кэшированием
        cache_key = "site_settings"
        site_settings = cache.get(cache_key)

        if not site_settings:
            site_settings = SiteSettings.load()
            if site_settings:
                cache.set(cache_key, site_settings, 300)  # Кэш на 5 минут

        context["site_settings"] = site_settings

        # Добавляем базовые SEO данные
        context.setdefault("page_title", getattr(site_settings, "logo_text", "DPITS-CMS.RU") if site_settings else "DPITS-CMS.RU")
        context.setdefault("meta_description", getattr(site_settings, "seo_description", "") if site_settings else "")
        context.setdefault("meta_keywords", getattr(site_settings, "seo_keywords", "") if site_settings else "")

        return context


class ProfileView(MaintenanceMixin, BaseView, TemplateView):
    """
    Представление для страницы профиля пользователя.
    Отображает шаблон профиля с базовым контекстом.
    Требует аутентификации пользователя.
    """

    template_name = "main/profile.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет, аутентифицирован ли пользователь.
        """
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            from django.shortcuts import resolve_url
            return redirect_to_login(
                request.get_full_path(),
                login_url=resolve_url("accounts:login")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Добавляет данные контекста для страницы профиля.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Профиль",
                "meta_description": "Профиль пользователя",
                "user": self.request.user,
            }
        )
        return context


class IndexView(MaintenanceMixin, BaseView, TemplateView):
    """
    Представление для главной страницы сайта.
    Наследует функциональность обслуживания и базовые данные.
    """

    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        """
        Расширяет контекст данными для главной страницы.
        Включает рекомендуемые страницы и SEO-данные.
        """
        context = super().get_context_data(**kwargs)
        site_settings = context.get("site_settings")

        # Получаем рекомендуемые страницы для главной
        cache_key = "featured_pages"
        featured_pages = cache.get(cache_key)
        
        if not featured_pages:
            featured_pages = list(
                Page.objects.filter(show_on_site=True)
                .order_by("order", "title")[:6]
            )
            if featured_pages:
                cache.set(cache_key, featured_pages, 600)  # Кэш на 10 минут

        # Получаем три последние новости
        recent_news_list = []
        if News:
            try:
                recent_news_list = list(
                    News.objects.filter(is_active=True)
                    .order_by("-created_at")[:3]
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
                page_title = f"{site_settings.logo_text} - {site_settings.seo_title}" if site_settings.logo_text else site_settings.seo_title
            elif site_settings.logo_text:
                page_title = site_settings.logo_text

        meta_description = ""
        if site_settings:
            if site_settings.short_description:
                # Убираем HTML теги и ограничиваем длину
                meta_description = re.sub(r'<[^>]+>', '', str(site_settings.short_description))
                meta_description = meta_description[:160] if len(meta_description) > 160 else meta_description
            elif site_settings.seo_description:
                meta_description = site_settings.seo_description

        context.update(
            {
                "featured_pages": featured_pages,
                "recent_news_list": recent_news_list,
                "page_title": page_title,
                "meta_description": meta_description,
            }
        )

        return context

    @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
    @method_decorator(vary_on_cookie)  # Учитываем куки пользователя
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PageDetailView(MaintenanceMixin, BaseView, DetailView):
    """
    Представление для отображения детальной информации о странице.
    """

    model = Page
    template_name = "main/page_detail.html"
    context_object_name = "page"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """
        Возвращает только активные страницы (show_on_site=True).
        """
        return Page.objects.filter(show_on_site=True)

    def get_object(self, queryset=None):
        """
        Получает объект страницы или выбрасывает 404.
        """
        slug = self.kwargs.get(self.slug_url_kwarg)
        queryset = self.get_queryset()
        try:
            page = queryset.get(slug=slug)
            return page
        except Page.DoesNotExist:
            raise Http404("Страница не найдена")

    def get_context_data(self, **kwargs):
        """
        Добавляет SEO-данные и связанный контент.
        """
        context = super().get_context_data(**kwargs)
        page = self.object
        site_settings = context.get("site_settings")

        # Получаем предыдущую и следующую страницы
        prev_page = None
        next_page = None
        try:
            prev_page = (
                Page.objects.filter(
                    show_on_site=True,
                    order__lt=page.order
                )
                .order_by("-order", "-created_at")
                .first()
            )
            if not prev_page:
                prev_page = (
                    Page.objects.filter(
                        show_on_site=True,
                        created_at__lt=page.created_at
                    )
                    .order_by("-created_at")
                    .first()
                )
        except Exception:
            pass

        try:
            next_page = (
                Page.objects.filter(
                    show_on_site=True,
                    order__gt=page.order
                )
                .order_by("order", "created_at")
                .first()
            )
            if not next_page:
                next_page = (
                    Page.objects.filter(
                        show_on_site=True,
                        created_at__gt=page.created_at
                    )
                    .order_by("created_at")
                    .first()
                )
        except Exception:
            pass

        # SEO-данные страницы
        page_title = page.display_title
        if site_settings and site_settings.logo_text:
            page_title = f"{page.display_title} - {site_settings.logo_text}"

        # Мета-описание
        meta_description = page.seo_description
        if not meta_description and page.content:
            meta_description = re.sub(r'<[^>]+>', '', str(page.content))
            meta_description = meta_description[:160] if len(meta_description) > 160 else meta_description

        context.update(
            {
                "page_title": page_title,
                "meta_description": meta_description,
                "meta_keywords": page.seo_keywords,
                "prev_page": prev_page,
                "next_page": next_page,
            }
        )

        return context

    @method_decorator(cache_page(60 * 10))  # Кэшируем на 10 минут
    @method_decorator(vary_on_cookie)  # Учитываем куки пользователя
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ContactView(MaintenanceMixin, BaseView, TemplateView):
    """
    Представление для страницы контактов.
    """

    template_name = "main/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = context.get("site_settings")

        page_title = "Контакты"
        if site_settings and site_settings.logo_text:
            page_title = f"Контакты - {site_settings.logo_text}"

        meta_description = "Контактная информация и способы связи"
        if site_settings and site_settings.seo_description:
            meta_description = site_settings.seo_description

        context.update(
            {
                "page_title": page_title,
                "meta_description": meta_description,
            }
        )
        return context


class AboutView(MaintenanceMixin, BaseView, TemplateView):
    """
    Представление для страницы "О нас".
    """

    template_name = "main/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = context.get("site_settings")

        page_title = "О нас"
        if site_settings and site_settings.logo_text:
            page_title = f"О нас - {site_settings.logo_text}"

        meta_description = "Информация о нашей компании и услугах"
        if site_settings:
            if site_settings.short_description:
                meta_description = re.sub(r'<[^>]+>', '', str(site_settings.short_description))
                meta_description = meta_description[:160] if len(meta_description) > 160 else meta_description
            elif site_settings.seo_description:
                meta_description = site_settings.seo_description

        context.update(
            {
                "page_title": page_title,
                "meta_description": meta_description,
            }
        )
        return context


def custom_404_view(request, exception):
    """
    Кастомная страница 404 ошибки.
    """
    site_settings = SiteSettings.load()
    context = {
        "site_settings": site_settings,
        "exception": exception,
        "page_title": "Страница не найдена (404)",
        "meta_description": "Запрашиваемая страница не найдена",
    }
    return render(
        request,
        "main/404.html",
        context,
        status=404,
    )


def custom_500_view(request):
    """
    Кастомная страница 500 ошибки.
    """
    site_settings = SiteSettings.load()
    context = {
        "site_settings": site_settings,
        "page_title": "Ошибка сервера (500)",
        "meta_description": "Произошла внутренняя ошибка сервера",
    }
    return render(
        request,
        "main/500.html",
        context,
        status=500,
    )
