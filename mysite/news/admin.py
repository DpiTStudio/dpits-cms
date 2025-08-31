from django.contrib import admin
from .models import News, NewsCategory
from .forms import NewsCategoryForm, NewsForm


class NewsCategoryAdmin(admin.ModelAdmin):
    form = NewsCategoryForm
    list_display = [
        "name",
        "is_active",
        "order",
    ]
    list_editable = [
        "order",
        "is_active",
    ]
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ["is_active"]
    search_fields = ["name"]

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"


class NewsAdmin(admin.ModelAdmin):
    form = NewsForm
    list_display = [
        "title",
        "category",
        "is_active",
        "created_at",
        "views",
    ]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = [
        "category",
        "is_active",
        "created_at",
    ]
    search_fields = [
        "title",
        "content",
    ]
    date_hierarchy = "created_at"

    # Поля для отображения в админке
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "image",
                    "content",
                    "views",
                )
            },
        ),
        (
            "SEO настройки",
            {
                "fields": (
                    "meta_title",
                    "meta_keywords",
                    "meta_description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Дополнительно",
            {
                "fields": ("is_active",),
                "classes": ("collapse",),
            },
        ),
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(News, NewsAdmin)
