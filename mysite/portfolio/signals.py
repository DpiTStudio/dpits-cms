# portfolio/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from .models import PortfolioItem
from news.models import News, NewsCategory


@receiver(post_save, sender=PortfolioItem)
def create_news_from_portfolio(sender, instance, created, **kwargs):
    """
    Автоматически создает новость при добавлении новой работы в портфолио.
    """
    if created and instance.status == "published":
        try:
            # 1. Находим или создаем специальную категорию для новостей портфолио
            portfolio_category, _ = NewsCategory.objects.get_or_create(
                name="Портфолио",
                defaults={
                    "slug": "portfolio",
                    "description": "Новости о новых работах в портфолио",
                    "show_in_menu": True,
                    "order": 10,
                    "is_active": True,
                },
            )

            # 2. Создаем новость
            news = News.objects.create(
                title=f"Новая работа в портфолио: {instance.title}",
                slug=f"portfolio-{instance.slug}",
                category=portfolio_category,
                image=instance.image if instance.image else None,
                short_description=instance.short_description,
                content=f"""
                <h3>Добавлена новая работа в портфолио</h3>
                <p><strong>Название:</strong> {instance.title}</p>
                <p><strong>Категория:</strong> {instance.category.name}</p>
                <p><strong>Краткое описание:</strong> {instance.short_description}</p>
                <p><strong>Технологии:</strong> {instance.technologies}</p>
                <p><strong>Дата проекта:</strong> {instance.project_date}</p>
                
                <h4>Посмотреть работу:</h4>
                <p><a href="{instance.get_absolute_url()}">Перейти к работе</a></p>
                """,
                is_active=True,
            )

            # 3. Логируем создание
            print(f"Создана новость для портфолио: {news.title}")

        except Exception as e:
            print(f"Ошибка при создании новости для портфолио: {e}")
