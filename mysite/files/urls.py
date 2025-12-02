# urls.py
# Конфигурация URL для приложения files
# Определяет маршруты (URL patterns) для работы с файлами

from django.urls import path
from . import views

# Пространство имен для URL приложения files
app_name = "files"

# Список URL-маршрутов приложения files
urlpatterns = [
    # Список всех файлов
    path("", views.FileListView.as_view(), name="file_list"),
    
    # Детальная информация о файле
    path("<int:pk>/", views.FileDetailView.as_view(), name="file_detail"),
    
    # Скачивание файла
    path("<int:pk>/download/", views.FileDownloadView.as_view(), name="file_download"),
    
    # Загрузка нового файла
    path("upload/", views.FileUploadView.as_view(), name="file_upload"),
    
    # Редактирование файла
    path("<int:pk>/edit/", views.FileUpdateView.as_view(), name="file_edit"),
    
    # Удаление файла
    path("<int:pk>/delete/", views.FileDeleteView.as_view(), name="file_delete"),
    
    # Список категорий файлов
    path("categories/", views.FileCategoryListView.as_view(), name="category_list"),
    
    # Детальная информация о категории
    path("categories/<int:pk>/", views.FileCategoryDetailView.as_view(), name="category_detail"),
]

