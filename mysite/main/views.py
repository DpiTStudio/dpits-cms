# main/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from .models import SiteSettings, Page


class BaseView:
    """
    Базовый класс для всех представлений.
    Содержит общую логику для наследования.
    """

    def get_context_data(self, **kwargs):
        """
        Добавляет общие данные контекста для всех страниц.
        """
        context = super().get_context_data(**kwargs)

        # Получаем настройки сайта (с кэшированием на уровне представления)
        cache_key = f"site_settings_{self.__class__.__name__}"
        site_settings = cache.get(cache_key)

        if not site_settings:
            site_settings = SiteSettings.load()
            cache.set(cache_key, site_settings, 300)  # Кэш на 5 минут

        context["site_settings"] = site_settings

        # Проверяем, закрыт ли сайт
        if site_settings and site_settings.site_closed:
            # Для закрытого сайта используем специальный шаблон
            self.template_name = "main/site_closed.html"
            context["closure_message"] = site_settings.closure_message

        return context


class MaintenanceMixin:
    """
    Миксин для проверки статуса обслуживания сайта.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Перехватывает запрос и проверяет, не закрыт ли сайт.
        """
        site_settings = SiteSettings.load()

        if site_settings.site_closed and not request.user.is_staff:
            # Для закрытого сайта показываем специальную страницу
            return render(
                request, "main/site_closed.html", {"site_settings": site_settings}
            )

        return super().dispatch(request, *args, **kwargs)


class IndexView(MaintenanceMixin, BaseView, TemplateView):
    """
    Представление для главной страницы сайта.
    Наследует функциональность обслуживания и базовые данные.
    """

    template_name = "main/index.html"

    def get_context_data(self, **kwargs):
        """
        Расширяет контекст данными для главной страницы.
        """
        context = super().get_context_data(**kwargs)

        # Получаем featured страницы для главной
        featured_pages = Page.objects.filter(show_on_site=True).order_by(
            "order", "title"
        )[:6]  # Ограничиваем количество

        context.update(
            {
                "featured_pages": featured_pages,
                "page_title": "Главная",
                "meta_description": getattr(
                    context.get("site_settings"), "short_description", ""
                ),
            }
        )

        return context

    @method_decorator(cache_page(60 * 15))  # Кэшируем на 15 минут
    @method_decorator(vary_on_cookie)
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

    def get_context_data(self, **kwargs):
        """
        Добавляет SEO-данные и связанный контент.
        """
        context = super().get_context_data(**kwargs)
        page = self.object

        # SEO-данные
        context.update(
            {
                "page_title": page.display_title,
                "meta_description": page.seo_description or page.content[:160],
                "meta_keywords": page.seo_keywords,
            }
        )

        return context

    @method_decorator(cache_page(60 * 10))  # Кэшируем на 10 минут
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ContactView(MaintenanceMixin, BaseView, TemplateView):
    """
    Представление для страницы контактов.
    """

    template_name = "main/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Контакты",
                "meta_description": "Контактная информация и способы связи",
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
        context.update(
            {
                "page_title": "О нас",
                "meta_description": "Информация о нашей компании и услугах",
            }
        )
        return context


def custom_404_view(request, exception):
    """
    Кастомная страница 404 ошибки.
    """
    site_settings = SiteSettings.load()
    return render(
        request,
        "main/404.html",
        {"site_settings": site_settings, "exception": exception},
        status=404,
    )


def custom_500_view(request):
    """
    Кастомная страница 500 ошибки.
    """
    site_settings = SiteSettings.load()
    return render(
        request, "main/500.html", {"site_settings": site_settings}, status=500
    )
