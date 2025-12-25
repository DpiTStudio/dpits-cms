# news/admin.py
from django.contrib import admin  # Импорт админ-панели Django
from .models import NewsCategory, News  # Импорт моделей новостей


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления категориями новостей.

    Предоставляет интерфейс для создания, редактирования и просмотра категорий новостей
    в административной панели Django. Включает настройки отображения, SEO-параметры
    и управление активностью категории.
    """

    list_display = ["name", "slug", "show_in_menu", "order", "is_active"]
    """
    Определяет столбцы, отображаемые в списке категорий в админке.

    Поля:
        - name: Название категории.
        - slug: Уникальный идентификатор в URL.
        - show_in_menu: Отображается ли категория в меню.
        - order: Порядок отображения.
        - is_active: Активна ли категория.
    """

    list_editable = ["show_in_menu", "order", "is_active"]
    """
    Позволяет редактировать указанные поля прямо из списка объектов,
    без необходимости заходить в форму редактирования.
    """

    prepopulated_fields = {"slug": ("name",)}
    """
    Автоматически генерирует значение поля 'slug' на основе поля 'name'.
    Обеспечивает удобство при создании новых категорий.
    """

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": ("name", "slug", "image", "description"),
            },
        ),
        (
            "Настройки отображения",
            {
                "fields": ("show_in_menu", "order", "is_active"),
            },
        ),
        (
            "SEO оптимизация",
            {
                "fields": ("seo_title", "seo_keywords", "seo_description"),
            },
        ),
    )
    """
    Организует поля формы редактирования на вкладки (группы) для удобства восприятия.

    Группы:
        - Основная информация: базовые данные о категории.
        - Настройки отображения: параметры видимости и порядка.
        - SEO оптимизация: мета-теги для поисковой оптимизации.
    """


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления новостями.

    Предоставляет интерфейс для просмотра, редактирования и фильтрации новостей
    в админке Django. Настраивает отображение полей, группировку в разделы
    и определяет параметры редактирования.
    """

    list_display = [
        "title",
        "category",
        "views",
        "is_active",
        "created_at",
        "clear_views_button",
    ]
    """
    Поля, отображаемые в списке новостей:
        - title: Заголовок новости.
        - category: Категория новости.
        - views: Количество просмотров.
        - is_active: Статус активности.
        - created_at: Дата создания.
        - clear_views_button: Кнопка для сброса просмотров.
    """

    list_filter = ["category", "is_active", "created_at"]
    """
    Фильтры, доступные в боковой панели админки:
        - category: Фильтрация по категории.
        - is_active: Фильтрация по статусу активности.
        - created_at: Фильтрация по дате создания.
    """

    list_editable = ["is_active"]
    """
    Позволяет редактировать статус активности прямо в списке новостей.
    """

    prepopulated_fields = {"slug": ("title",)}
    """
    Автоматически заполняет поле 'slug' на основе заголовка новости.
    Обеспечивает ЧПУ (человекопонятные URL).
    """

    readonly_fields = ["views", "created_at", "updated_at"]
    """
    Поля, доступные только для чтения в форме редактирования:
        - views: Количество просмотров (управляется через действия).
        - created_at: Дата создания.
        - updated_at: Дата последнего обновления.
    """

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "image",
                    "short_description",
                    "content",
                )
            },
        ),
        ("Статистика", {"fields": ("views", "created_at", "updated_at")}),
        ("SEO настройки", {"fields": ("seo_title", "seo_keywords", "seo_description")}),
        ("Статус", {"fields": ("is_active",)}),
    )
    """
    Группировка полей в форме редактирования новости:
        - Основная информация: заголовок, категория, изображение, текст.
        - Статистика: метрики просмотров и даты.
        - SEO настройки: мета-теги для поисковой оптимизации.
        - Статус: активность публикации.
    """

    actions = ["clear_views_action"]
    """
    Дополнительные действия, доступные для выборки новостей.
    clear_views_action позволяет сбросить просмотры у выбранных записей.
    """

    def clear_views_button(self, obj):
        """
        Отображает кнопку «Очистить» в списке новостей для сброса просмотров.

        Аргументы:
            obj (News): Экземпляр модели новости.

        Возвращает:
            str: HTML-код кнопки с ссылкой на страницу сброса просмотров.
        """
        from django.utils.html import format_html

        return format_html(
            '<a class="button" href="{}" style="padding: 5px 10px; background: #417690; color: white; '
            'text-decoration: none; border-radius: 3px;">Очистить</a>',
            f"{obj.pk}/clear_views/",
        )

    clear_views_button.short_description = "Очистить просмотры"
    clear_views_button.allow_tags = True  # Устаревшее, но оставлено для совместимости

    def get_urls(self):
        """
        Добавляет пользовательский URL для обработки сброса просмотров.

        Возвращает:
            list: Список URL-маршрутов, включая стандартные и добавленные.
        """
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/clear_views/",
                self.admin_site.admin_view(self.clear_views),
                name="news_clear_views",
            ),
        ]
        return custom_urls + urls

    def clear_views(self, request, object_id, *args, **kwargs):
        """
        Обработчик сброса количества просмотров для конкретной новости.

        Аргументы:
            request (HttpRequest): Объект запроса.
            object_id (str): Идентификатор новости.
            *args, **kwargs: Дополнительные аргументы.

        Возвращает:
            HttpResponse: Редирект на страницу списка новостей с сообщением об успехе.
        """
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages

        news = get_object_or_404(News, pk=object_id)
        old_views = news.views
        news.views = 0
        news.save()

        messages.success(
            request,
            f'Количество просмотров для новости "{news.title}" сброшено с {old_views} до 0.',
        )
        return redirect("admin:news_news_changelist")

    @admin.action(description="Сбросить просмотры у выбранных новостей")
    def clear_views_action(self, request, queryset):
        """
        Массовое действие для сброса просмотров у выбранных новостей.

        Аргументы:
            request (HttpRequest): Объект запроса.
            queryset (QuerySet): Выбранные в админке объекты новостей.

        Возвращает:
            None: Сообщение выводится через систему сообщений Django.
        """

        updated_count = queryset.update(views=0)
        self.message_user(
            request, f"Количество просмотров сброшено для {updated_count} новостей."
        )

    clear_views_action.short_description = "Сбросить просмотры у выбранных новостей"  # type: ignore
