# Migration: add NewsTag model and tags field to News
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0008_alter_news_category_on_delete_protect"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Название тега"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(unique=True, verbose_name="Слаг"),
                ),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="news",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="news",
                to="news.newstag",
                verbose_name="Теги",
            ),
        ),
    ]
