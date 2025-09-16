from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    phone1 = models.CharField(_("Телефон 1"), max_length=20, blank=True)
    phone2 = models.CharField(_("Телефон 2"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), max_length=255, blank=True)
    logo = models.ImageField(_("Логотип"), upload_to="logos/", blank=True)
    logo_text = models.CharField(_("Текст логотипа"), max_length=100, blank=True)
    slogan = models.CharField(_("Слоган в шапке"), max_length=255, blank=True)
    motto = models.CharField(_("Девиз сайта"), max_length=255, blank=True)
    short_description = models.TextField(
        _("Краткое описание"), blank=True
    )  # Убрали config_name="extends"
    site_closed = models.BooleanField(_("Сайт закрыт"), default=False)
    closure_message = models.TextField(_("Сообщение при закрытии"), blank=True)

    class Meta:
        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")

    def save(self, *args, **kwargs):
        # Разрешаем создавать только одну запись настроек
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Может существовать только одна запись настроек")
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Метод для загрузки единственной записи настроек
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Настройки сайта"


class Page(models.Model):
    title = models.CharField(_("Заголовок"), max_length=200)
    slug = models.SlugField(_("URL"), unique=True)
    content = models.TextField(
        _("Содержание"), blank=True
    )  # Убрали config_name="extends"
    show_in_menu = models.BooleanField(_("Показывать в меню"), default=True)
    show_on_site = models.BooleanField(_("Показывать на сайте"), default=True)
    order = models.IntegerField(_("Порядок"), default=0)
    seo_title = models.CharField(_("SEO заголовок"), max_length=200, blank=True)
    seo_keywords = models.CharField(_("SEO ключевые слова"), max_length=200, blank=True)
    seo_description = models.CharField(_("SEO описание"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("Страница")
        verbose_name_plural = _("Страницы")
        ordering = ["order", "title"]

    @classmethod
    def load(cls):
        # Метод для загрузки единственной записи настроек
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.title
