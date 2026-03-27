# Generated migration: change on_delete for News.category from CASCADE to PROTECT
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0007_news_hero_image_news_hero_is_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="news",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="news.newscategory",
                verbose_name="Категория",
            ),
        ),
    ]
