from django.db import models
from tinymce.models import HTMLField


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    logo = models.ImageField(upload_to="news/categories/", verbose_name="Логотип")
    meta_title = models.CharField(max_length=200, verbose_name="Мета заголовок")
    meta_keywords = models.CharField(max_length=200, verbose_name="Ключевые слова")
    description = models.TextField(verbose_name="Описание")
    content = HTMLField(verbose_name="Описание на странице", default="<p>Описание</p>")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, verbose_name="Категория"
    )
    image = models.ImageField(upload_to="news/images/", verbose_name="Изображение")
    meta_title = models.CharField(max_length=200, verbose_name="Мета заголовок")
    meta_keywords = models.CharField(max_length=200, verbose_name="Ключевые слова")
    meta_description = models.CharField(max_length=255, verbose_name="Мета описание")
    content = HTMLField(verbose_name="Контент", default="<p>Контент сайта</p>")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        self.save()


class Comment(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="comments",  # ← это важно!
    )
    rating = models.IntegerField(default=0)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
