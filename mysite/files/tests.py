# tests.py
# Тесты для приложения files
# Содержит unit-тесты для проверки функциональности приложения

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import File, FileCategory

User = get_user_model()


class FileCategoryModelTest(TestCase):
    """
    Тесты для модели FileCategory.
    Проверяет создание и работу категорий файлов.
    """

    def setUp(self):
        """
        Настройка тестовых данных перед каждым тестом.
        Создает тестовую категорию.
        """
        self.category = FileCategory.objects.create(
            name="Тестовая категория",
            description="Описание тестовой категории",
            icon="fa-file",
            color="#007bff",
        )

    def test_category_creation(self):
        """
        Тест создания категории.
        Проверяет, что категория создается корректно.
        """
        self.assertEqual(self.category.name, "Тестовая категория")
        self.assertTrue(self.category.is_active)

    def test_category_str(self):
        """
        Тест строкового представления категории.
        Проверяет метод __str__.
        """
        self.assertEqual(str(self.category), "Тестовая категория")


class FileModelTest(TestCase):
    """
    Тесты для модели File.
    Проверяет создание и работу файлов.
    """

    def setUp(self):
        """
        Настройка тестовых данных перед каждым тестом.
        Создает тестового пользователя и категорию.
        """
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = FileCategory.objects.create(name="Тестовая категория")
        self.test_file = SimpleUploadedFile(
            "test.txt", b"file content", content_type="text/plain"
        )

    def test_file_creation(self):
        """
        Тест создания файла.
        Проверяет, что файл создается корректно.
        """
        file_obj = File.objects.create(
            name="Тестовый файл",
            original_name="test.txt",
            file=self.test_file,
            category=self.category,
            uploaded_by=self.user,
        )
        self.assertEqual(file_obj.name, "Тестовый файл")
        self.assertEqual(file_obj.uploaded_by, self.user)

    def test_file_human_readable_size(self):
        """
        Тест метода human_readable_size.
        Проверяет форматирование размера файла.
        """
        file_obj = File.objects.create(
            name="Тестовый файл",
            original_name="test.txt",
            file=self.test_file,
            file_size=1024,
        )
        self.assertIn("КБ", file_obj.human_readable_size)


class FileViewsTest(TestCase):
    """
    Тесты для представлений (views) файлов.
    Проверяет работу HTTP-запросов.
    """

    def setUp(self):
        """
        Настройка тестовых данных перед каждым тестом.
        Создает тестового пользователя, клиента и категорию.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = FileCategory.objects.create(name="Тестовая категория")

    def test_file_list_view(self):
        """
        Тест представления списка файлов.
        Проверяет доступность страницы списка файлов.
        """
        response = self.client.get(reverse("files:file_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "files/file_list.html")

    def test_file_upload_view_requires_login(self):
        """
        Тест представления загрузки файла.
        Проверяет, что требуется авторизация.
        """
        response = self.client.get(reverse("files:file_upload"))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

    def test_file_upload_view_authenticated(self):
        """
        Тест представления загрузки файла для авторизованного пользователя.
        Проверяет доступность страницы загрузки.
        """
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("files:file_upload"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "files/file_upload.html")

