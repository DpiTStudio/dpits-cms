from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from main.models import SiteSettings, Page, ManagedFile
from main.forms import ContactForm

User = get_user_model()


class SiteSettingsModelTest(TestCase):
    """Тесты для модели SiteSettings (Singleton)."""

    def setUp(self):
        # Очистим перед тестом
        SiteSettings.objects.all().delete()

    def test_singleton_behavior(self):
        """Проверяет, что SiteSettings ведет себя как синглтон."""
        settings1 = SiteSettings.load()
        self.assertEqual(settings1.pk, 1)

        settings2 = SiteSettings.load()
        self.assertEqual(settings2.pk, 1)
        self.assertEqual(SiteSettings.objects.count(), 1)

        # Попытка создать вторую запись через конструктор все равно перезапишет ID = 1 при сохранении
        settings3 = SiteSettings(title="Test settings 3")
        settings3.save()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.load().title, "Test settings 3")

    def test_validation(self):
        """Проверяет валидацию полей SiteSettings."""
        settings = SiteSettings.load()
        settings.site_closed = True
        settings.closure_message = ""
        # Должна быть ошибка: сайт закрыт, но нет сообщения о закрытии
        with self.assertRaises(ValidationError):
            settings.full_clean()

        settings.closure_message = "Технические работы"
        settings.full_clean()  # Теперь должно пройти успешно

        # Некорректный email
        settings.email = "invalidemail"
        with self.assertRaises(ValidationError):
            settings.full_clean()

        settings.email = "info@example.com"
        settings.full_clean()  # Теперь успешно


class PageModelTest(TestCase):
    """Тесты для модели Page."""

    def test_reserved_slug_validation(self):
        """Проверяет, что зарезервированные URL-адреса вызывают ошибку валидации."""
        page = Page(title="Admin Page", slug="admin", content="Some content")
        with self.assertRaises(ValidationError):
            page.full_clean()

        # Разрешенный slug
        page.slug = "regular-page"
        page.full_clean()  # Успешно

    def test_get_absolute_url(self):
        """Проверяет правильность генерации URL страницы."""
        page = Page.objects.create(title="About Us", slug="about-us", content="We are a company")
        expected_url = reverse("main:page_detail", kwargs={"slug": page.slug})
        self.assertEqual(page.get_absolute_url(), expected_url)

    def test_navigation_prev_next(self):
        """Проверяет методы получения предыдущей и следующей страниц."""
        page1 = Page.objects.create(title="Page 1", slug="page-1", content="Content 1", order=10)
        page2 = Page.objects.create(title="Page 2", slug="page-2", content="Content 2", order=20)
        page3 = Page.objects.create(title="Page 3", slug="page-3", content="Content 3", order=30)

        self.assertEqual(page2.get_previous_page().pk, page1.pk)
        self.assertEqual(page2.get_next_page().pk, page3.pk)

        self.assertIsNone(page1.get_previous_page())
        self.assertIsNone(page3.get_next_page())


class ContactFormTest(TestCase):
    """Тесты для формы ContactForm."""

    def test_valid_data(self):
        """Проверяет валидацию формы с корректными данными."""
        form = ContactForm(data={
            "name": "Иван",
            "contact": "ivan@example.com",
            "message": "Приветствую! Меня интересует ваш проект."
        })
        self.assertTrue(form.is_valid())

    def test_invalid_name(self):
        """Имя должно быть не менее 2 символов."""
        form = ContactForm(data={
            "name": "И",
            "contact": "ivan@example.com",
            "message": "Приветствую! Меня интересует ваш проект."
        })
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_invalid_message(self):
        """Сообщение должно быть не менее 10 символов."""
        form = ContactForm(data={
            "name": "Иван",
            "contact": "ivan@example.com",
            "message": "Коротко"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)


class ManagedFileTest(TestCase):
    """Тесты для вспомогательных методов ManagedFile."""

    def test_human_readable_size(self):
        """Проверяет форматирование размера файла."""
        f = ManagedFile(name="test.txt", file_path="dummy/path")
        
        f.file_size = 0
        self.assertEqual(f.human_readable_size, "0 B")
        
        f.file_size = 500
        self.assertEqual(f.human_readable_size, "500.00 B")

        f.file_size = 2048
        self.assertEqual(f.human_readable_size, "2.00 KB")

        f.file_size = 1048576 * 3
        self.assertEqual(f.human_readable_size, "3.00 MB")


class MainViewsTest(TestCase):
    """Тесты представлений (Views) приложения Main."""

    def setUp(self):
        self.client = Client()
        self.site_settings = SiteSettings.load()
        self.site_settings.title = "DpiTStudio CMS"
        self.site_settings.logo_text = "DPITS-CMS"
        self.site_settings.site_closed = False
        self.site_settings.save()

        self.page = Page.objects.create(
            title="О компании",
            slug="about-company",
            content="<p>Информация о компании</p>",
            show_on_site=True
        )

    def test_index_view(self):
        """Проверяет доступность главной страницы."""
        response = self.client.get(reverse("main:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DPITS-CMS")

    def test_page_detail_view(self):
        """Проверяет доступность детальной страницы контента."""
        response = self.client.get(self.page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "О компании")
        self.assertContains(response, "Информация о компании")

    def test_contacts_view(self):
        """Проверяет доступность страницы контактов."""
        response = self.client.get(reverse("main:contacts"))
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        """Проверяет доступность страницы 'О нас'."""
        response = self.client.get(reverse("main:about"))
        self.assertEqual(response.status_code, 200)

    def test_maintenance_mode(self):
        """Проверяет работу режима обслуживания (закрытого сайта)."""
        self.site_settings.site_closed = True
        self.site_settings.closure_message = "Сайт на обслуживании"
        self.site_settings.save()

        # Для неавторизованного пользователя
        response = self.client.get(reverse("main:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/site_closed.html")
        self.assertContains(response, "Сайт на обслуживании")
