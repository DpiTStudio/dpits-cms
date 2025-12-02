# views.py
# Представления (контроллеры) для приложения files
# Обрабатывает HTTP-запросы для работы с файлами

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from .models import File, FileCategory, FileVersion
from .forms import FileUploadForm, FileEditForm, FileSearchForm


class FileListView(ListView):
    """
    Представление для отображения списка файлов.
    Показывает все файлы с возможностью фильтрации и поиска.
    """

    model = File
    template_name = "files/file_list.html"
    context_object_name = "files"
    paginate_by = 20  # Количество файлов на странице

    def get_queryset(self):
        """
        Возвращает queryset файлов с применением фильтров и поиска.

        Returns:
            QuerySet: Отфильтрованный список файлов
        """
        queryset = File.objects.select_related("category", "uploaded_by").all()

        # Получаем параметры поиска из формы
        form = FileSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get("query")
            category = form.cleaned_data.get("category")
            public_only = form.cleaned_data.get("public_only", False)
            active_only = form.cleaned_data.get("active_only", True)

            # Поиск по названию, описанию и тегам
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(tags__icontains=query)
                    | Q(original_name__icontains=query)
                )

            # Фильтр по категории
            if category:
                queryset = queryset.filter(category=category)

            # Фильтр по публичности
            if public_only:
                queryset = queryset.filter(is_public=True)

            # Фильтр по активности
            if active_only:
                queryset = queryset.filter(is_active=True)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Args:
            **kwargs: Дополнительные аргументы

        Returns:
            dict: Контекст для шаблона
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = FileSearchForm(self.request.GET)
        context["categories"] = FileCategory.objects.filter(is_active=True)
        return context


class FileDetailView(DetailView):
    """
    Представление для отображения детальной информации о файле.
    Показывает полную информацию о файле и его версиях.
    """

    model = File
    template_name = "files/file_detail.html"
    context_object_name = "file"

    def get_queryset(self):
        """
        Возвращает queryset файлов с оптимизацией запросов.

        Returns:
            QuerySet: Оптимизированный queryset файлов
        """
        return File.objects.select_related("category", "uploaded_by").prefetch_related(
            "versions"
        )

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Args:
            **kwargs: Дополнительные аргументы

        Returns:
            dict: Контекст для шаблона
        """
        context = super().get_context_data(**kwargs)
        # Получаем версии файла
        context["versions"] = self.object.versions.all().order_by("-version_number")
        return context


class FileDownloadView(DetailView):
    """
    Представление для скачивания файла.
    Отдает файл пользователю и увеличивает счетчик скачиваний.
    """

    model = File

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для скачивания файла.

        Args:
            request: HTTP-запрос
            *args: Дополнительные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            FileResponse: HTTP-ответ с файлом

        Raises:
            Http404: Если файл не найден или недоступен
        """
        file_obj = self.get_object()

        # Проверяем доступ к файлу
        if not file_obj.is_public and not request.user.is_authenticated:
            raise Http404(_("Файл недоступен"))

        if not file_obj.is_active:
            raise Http404(_("Файл неактивен"))

        # Проверяем существование файла
        if not file_obj.file:
            raise Http404(_("Файл не найден"))

        # Увеличиваем счетчик скачиваний
        file_obj.increment_download_count()

        # Отдаем файл
        try:
            response = FileResponse(
                file_obj.file.open("rb"),
                as_attachment=True,
                filename=file_obj.original_name or file_obj.name,
            )
            return response
        except Exception:
            raise Http404(_("Ошибка при открытии файла"))


class FileUploadView(LoginRequiredMixin, CreateView):
    """
    Представление для загрузки нового файла.
    Требует авторизации пользователя.
    """

    model = File
    form_class = FileUploadForm
    template_name = "files/file_upload.html"
    success_url = reverse_lazy("files:file_list")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму.
        Сохраняет файл и связывает его с текущим пользователем.

        Args:
            form: Валидная форма

        Returns:
            HttpResponseRedirect: Перенаправление на страницу успеха
        """
        # Связываем файл с текущим пользователем
        form.instance.uploaded_by = self.request.user

        # Сохраняем оригинальное имя файла
        if not form.instance.original_name and form.cleaned_data.get("file"):
            form.instance.original_name = form.cleaned_data["file"].name

        messages.success(self.request, _("Файл успешно загружен"))
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обрабатывает невалидную форму.
        Показывает сообщения об ошибках.

        Args:
            form: Невалидная форма

        Returns:
            HttpResponse: Ответ с формой и ошибками
        """
        messages.error(self.request, _("Ошибка при загрузке файла. Проверьте форму."))
        return super().form_invalid(form)


class FileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования файла.
    Требует авторизации пользователя.
    """

    model = File
    form_class = FileEditForm
    template_name = "files/file_edit.html"
    success_url = reverse_lazy("files:file_list")

    def get_queryset(self):
        """
        Возвращает queryset файлов с проверкой прав доступа.

        Returns:
            QuerySet: Queryset файлов
        """
        queryset = super().get_queryset()
        # Пользователь может редактировать только свои файлы или быть администратором
        if not self.request.user.is_staff:
            queryset = queryset.filter(uploaded_by=self.request.user)
        return queryset

    def form_valid(self, form):
        """
        Обрабатывает валидную форму.

        Args:
            form: Валидная форма

        Returns:
            HttpResponseRedirect: Перенаправление на страницу успеха
        """
        messages.success(self.request, _("Файл успешно обновлен"))
        return super().form_valid(form)


class FileDeleteView(LoginRequiredMixin, DeleteView):
    """
    Представление для удаления файла.
    Требует авторизации пользователя.
    """

    model = File
    template_name = "files/file_confirm_delete.html"
    success_url = reverse_lazy("files:file_list")

    def get_queryset(self):
        """
        Возвращает queryset файлов с проверкой прав доступа.

        Returns:
            QuerySet: Queryset файлов
        """
        queryset = super().get_queryset()
        # Пользователь может удалять только свои файлы или быть администратором
        if not self.request.user.is_staff:
            queryset = queryset.filter(uploaded_by=self.request.user)
        return queryset

    def delete(self, request, *args, **kwargs):
        """
        Обрабатывает удаление файла.

        Args:
            request: HTTP-запрос
            *args: Дополнительные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            HttpResponseRedirect: Перенаправление на страницу успеха
        """
        messages.success(self.request, _("Файл успешно удален"))
        return super().delete(request, *args, **kwargs)


class FileCategoryListView(ListView):
    """
    Представление для отображения списка категорий файлов.
    Показывает все активные категории.
    """

    model = FileCategory
    template_name = "files/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        """
        Возвращает queryset активных категорий.

        Returns:
            QuerySet: Список активных категорий
        """
        return FileCategory.objects.filter(is_active=True).order_by("order", "name")


class FileCategoryDetailView(DetailView):
    """
    Представление для отображения детальной информации о категории.
    Показывает все файлы в категории.
    """

    model = FileCategory
    template_name = "files/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Args:
            **kwargs: Дополнительные аргументы

        Returns:
            dict: Контекст для шаблона
        """
        context = super().get_context_data(**kwargs)
        # Получаем файлы в категории
        context["files"] = (
            self.object.files.filter(is_active=True)
            .select_related("uploaded_by")
            .order_by("-created_at")
        )
        return context

