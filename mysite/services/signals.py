# services/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service
from news.models import News, NewsCategory


@receiver(post_save, sender=Service)
def create_news_from_service(sender, instance, created, **kwargs):
    """
    Автоматически создает или обновляет новость при добавлении/обновлении услуги.
    """
    # Создаем новость только если услуга отображается
    if not instance.is_displayed:
        return

    try:
        # Получаем или создаем категорию новостей на основе категории услуги
        service_category = instance.category

        # Создаем slug для категории новостей на основе категории услуги
        news_category_slug = f"services-{service_category.slug}"

        # Находим или создаем категорию новостей
        news_category, _ = NewsCategory.objects.get_or_create(
            slug=news_category_slug,
            defaults={
                "name": f"Услуги: {service_category.name}",
                "description": f"Новости об услугах в категории {service_category.name}",
                "show_in_menu": True,
                "order": 20,
                "is_active": True,
            },
        )

        # Создаем slug для новости
        news_slug = f"service-{instance.slug}"

        if created:
            # Создаем новую новость при добавлении услуги
            news_title = f"Добавлена новая услуга: {instance.name}"
            news_content = create_news_content(instance, is_new=True)
        else:
            # Обновляем существующую новость или создаем новую при обновлении услуги
            news_title = f"Обновлена услуга: {instance.name}"
            news_content = create_news_content(instance, is_new=False)

            # Проверяем, существует ли уже новость об этой услуге
            existing_news = News.objects.filter(slug=news_slug).first()
            if existing_news:
                # Обновляем существующую новость
                existing_news.title = news_title
                existing_news.content = news_content
                existing_news.short_description = instance.short_description or ""
                if instance.icon:
                    existing_news.image = instance.icon
                existing_news.save()
                print(f"Обновлена новость для услуги: {existing_news.title}")
                return

        # Создаем новую новость
        news = News.objects.create(
            title=news_title,
            slug=news_slug,
            category=news_category,
            image=instance.icon if instance.icon else None,
            short_description=instance.short_description or "",
            content=news_content,
            is_active=True,
        )

        action = "Создана" if created else "Обновлена"
        print(f"{action} новость для услуги: {news.title}")

    except Exception as e:
        print(f"Ошибка при создании/обновлении новости для услуги: {e}")


def create_news_content(service, is_new=True):
    """
    Генерирует HTML-контент для новости на основе данных услуги.
    """
    action_text = "Добавлена новая услуга" if is_new else "Обновлена услуга"

    # Формируем информацию о цене
    price_html = f'<p><strong>Цена:</strong> {service.get_price_display()}</p>'

    # Формируем информацию о возможности заказа
    can_order_html = (
        '<p><strong>Статус:</strong> <span style="color: green;">✓ Можно заказать</span></p>'
        if service.can_order
        else '<p><strong>Статус:</strong> <span style="color: red;">✗ Заказ временно недоступен</span></p>'
    )

    # Формируем описание
    description_html = ""
    if service.description:
        description_html = f"""
        <div class="service-description">
            <h3>Описание услуги</h3>
            {service.description}
        </div>
        """

    # Формируем ссылку на услугу
    try:
        service_url = service.get_absolute_url()
        link_html = f"""
        <div class="service-actions mt-4">
            <a href="{service_url}" class="btn btn-primary">
                <i class="fas fa-external-link-alt"></i> Посмотреть детали услуги
            </a>
        </div>
        """
    except:
        # Если URL-маршруты еще не настроены, не добавляем ссылку
        link_html = ""

    content = f"""
    <div class="service-news">
        <h2>{action_text}: {service.name}</h2>
        
        <div class="service-info">
            <p><strong>Категория:</strong> {service.category.name}</p>
            {price_html}
            {can_order_html}
        </div>
        
        {description_html}
        
        {link_html}
    </div>
    """

    return content
