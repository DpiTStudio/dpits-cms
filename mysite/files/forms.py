# forms.py
# Формы для приложения files
# Определяет формы для загрузки и редактирования файлов

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import File, FileCategory


class FileUploadForm(forms.ModelForm):
    """
    Форма для загрузки нового файла.
    Позволяет пользователю загрузить файл с указанием категории и описания.
    """

    class Meta:
        """Метаданные формы."""

        model = File
        fields = ["name", "file", "category", "description", "tags", "is_public"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Введите название файла"),
                }
            ),
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "*/*",  # Принимаем все типы файлов
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("Введите описание файла"),
                }
            ),
            "tags": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Теги через запятую"),
                }
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": _("Название файла"),
            "file": _("Файл"),
            "category": _("Категория"),
            "description": _("Описание"),
            "tags": _("Теги"),
            "is_public": _("Публичный доступ"),
        }
        help_texts = {
            "name": _("Отображаемое название файла"),
            "file": _("Выберите файл для загрузки (максимум 100 МБ)"),
            "category": _("Выберите категорию файла"),
            "description": _("Подробное описание содержимого файла"),
            "tags": _("Теги через запятую для удобного поиска"),
            "is_public": _("Разрешить публичный доступ к файлу"),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        Настраивает queryset для категорий (только активные).
        """
        super().__init__(*args, **kwargs)
        # Показываем только активные категории
        self.fields["category"].queryset = FileCategory.objects.filter(is_active=True)

    def clean_file(self):
        """
        Валидация загружаемого файла.
        Проверяет размер и тип файла.

        Returns:
            UploadedFile: Валидный файл

        Raises:
            ValidationError: Если файл не прошел валидацию
        """
        file = self.cleaned_data.get("file")

        if not file:
            raise ValidationError(_("Необходимо выбрать файл для загрузки"))

        # Проверка размера файла (максимум 100 МБ)
        max_size = 100 * 1024 * 1024  # 100 МБ в байтах
        if file.size > max_size:
            raise ValidationError(
                _("Размер файла не должен превышать 100 МБ. Текущий размер: {} МБ").format(
                    file.size / (1024 * 1024)
                )
            )

        # Сохраняем оригинальное имя файла
        if not self.instance.original_name:
            self.instance.original_name = file.name

        return file

    def clean_tags(self):
        """
        Очистка и валидация тегов.
        Удаляет лишние пробелы и дубликаты.

        Returns:
            str: Очищенные теги через запятую
        """
        tags = self.cleaned_data.get("tags", "")
        if tags:
            # Разделяем по запятой, убираем пробелы, удаляем пустые
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            # Удаляем дубликаты, сохраняя порядок
            unique_tags = list(dict.fromkeys(tag_list))
            return ", ".join(unique_tags)
        return ""


class FileEditForm(forms.ModelForm):
    """
    Форма для редактирования существующего файла.
    Позволяет изменить метаданные файла (название, описание, категорию и т.д.).
    """

    class Meta:
        """Метаданные формы."""

        model = File
        fields = ["name", "category", "description", "tags", "is_public", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Введите название файла"),
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("Введите описание файла"),
                }
            ),
            "tags": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Теги через запятую"),
                }
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": _("Название файла"),
            "category": _("Категория"),
            "description": _("Описание"),
            "tags": _("Теги"),
            "is_public": _("Публичный доступ"),
            "is_active": _("Активен"),
        }
        help_texts = {
            "name": _("Отображаемое название файла"),
            "category": _("Выберите категорию файла"),
            "description": _("Подробное описание содержимого файла"),
            "tags": _("Теги через запятую для удобного поиска"),
            "is_public": _("Разрешить публичный доступ к файлу"),
            "is_active": _("Показывать файл в списке"),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        Настраивает queryset для категорий (только активные).
        """
        super().__init__(*args, **kwargs)
        # Показываем только активные категории
        self.fields["category"].queryset = FileCategory.objects.filter(is_active=True)

    def clean_tags(self):
        """
        Очистка и валидация тегов.
        Удаляет лишние пробелы и дубликаты.

        Returns:
            str: Очищенные теги через запятую
        """
        tags = self.cleaned_data.get("tags", "")
        if tags:
            # Разделяем по запятой, убираем пробелы, удаляем пустые
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            # Удаляем дубликаты, сохраняя порядок
            unique_tags = list(dict.fromkeys(tag_list))
            return ", ".join(unique_tags)
        return ""


class FileCategoryForm(forms.ModelForm):
    """
    Форма для создания и редактирования категории файлов.
    Позволяет управлять категориями файлов.
    """

    class Meta:
        """Метаданные формы."""

        model = FileCategory
        fields = ["name", "description", "icon", "color", "order", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Введите название категории"),
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Введите описание категории"),
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Например: fa-file, fa-image"),
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                    "placeholder": _("#007bff"),
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": _("Название категории"),
            "description": _("Описание"),
            "icon": _("Иконка"),
            "color": _("Цвет"),
            "order": _("Порядок"),
            "is_active": _("Активна"),
        }
        help_texts = {
            "name": _("Уникальное название категории"),
            "description": _("Подробное описание назначения категории"),
            "icon": _("CSS класс иконки (например: fa-file, fa-image)"),
            "color": _("Цвет в формате HEX (например: #007bff)"),
            "order": _("Порядок отображения категории в списке"),
            "is_active": _("Показывать категорию в интерфейсе"),
        }

    def clean_name(self):
        """
        Валидация названия категории.
        Проверяет уникальность названия.

        Returns:
            str: Валидное название категории

        Raises:
            ValidationError: Если название уже существует
        """
        name = self.cleaned_data.get("name")
        if name:
            # Проверяем уникальность (исключая текущий объект)
            qs = FileCategory.objects.filter(name=name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_("Категория с таким названием уже существует"))
        return name

    def clean_color(self):
        """
        Валидация цвета.
        Проверяет формат HEX цвета.

        Returns:
            str: Валидный цвет в формате HEX

        Raises:
            ValidationError: Если цвет в неправильном формате
        """
        color = self.cleaned_data.get("color", "")
        if color:
            # Проверяем формат HEX (#RRGGBB)
            if not color.startswith("#") or len(color) != 7:
                raise ValidationError(_("Цвет должен быть в формате HEX (например: #007bff)"))
            try:
                # Проверяем, что это валидный HEX
                int(color[1:], 16)
            except ValueError:
                raise ValidationError(_("Некорректный формат цвета"))
        return color


class FileSearchForm(forms.Form):
    """
    Форма для поиска файлов.
    Позволяет искать файлы по названию, описанию, тегам и категории.
    """

    # Поисковый запрос
    query = forms.CharField(
        label=_("Поиск"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Введите поисковый запрос"),
            }
        ),
    )

    # Категория для фильтрации
    category = forms.ModelChoiceField(
        label=_("Категория"),
        required=False,
        queryset=FileCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label=_("Все категории"),
    )

    # Только публичные файлы
    public_only = forms.BooleanField(
        label=_("Только публичные"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    # Только активные файлы
    active_only = forms.BooleanField(
        label=_("Только активные"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

