# ============================================================================================= #
# ФАЙЛ: FORMS.PY                                                                                #
# ОПИСАНИЕ:                                                                                     #
# Определяет HTML-формы для ввода данных пользователями. Используется для взаимодействия        #
# с клиентами (создание заказов, отзывов, редактирование профиля).                              #
#                                                                                               #
# НЮАНСЫ И ФУНКЦИОНАЛ:                                                                          #
# 1. ModelForms: Все формы базируются на моделях (Order, Review, Client), что упрощает          #
#    валидацию и сохранение данных.                                                             #
# 2. Стилизация виджетов:                                                                       #
#    - Используются кастомные виджеты (widgets) для добавления CSS-классов Bootstrap            #
#      (form-control, form-select) и плейсхолдеров.                                             #
# 3. Кастомная валидация:                                                                       #
#    - clean_budget: Запрет отрицательных значений бюджета.                                     #
#    - clean_title: Минимальная длина заголовка.                                                #
#    - clean_rating: Проверка допустимых значений рейтинга (1-5).                               #
# 4. Вспомогательные формы:                                                                     #
#    - OrderMessageForm: Для отправки сообщений в чате заказа (с поддержкой файлов).            #
#    - PortfolioSearchForm: Форма поиска с динамическим списком категорий.                      #
# ============================================================================================= #
# portfolio/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderMessage, PortfolioReview, Client


class OrderForm(forms.ModelForm):
    """Форма создания заказа"""

    class Meta:
        model = Order
        fields = [
            "title",
            "description",
            "budget",
            "deadline",
            "requirements_file",
            "additional_notes",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название вашего проекта",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Подробное описание проекта...",
                    "rows": 6,
                }
            ),
            "budget": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "10000"}
            ),
            "deadline": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "additional_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Дополнительная информация...",
                    "rows": 4,
                }
            ),
            "requirements_file": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "title": _("Название проекта"),
            "description": _("Описание проекта"),
            "budget": _("Бюджет (руб)"),
            "deadline": _("Срок выполнения"),
            "requirements_file": _("Файл требований"),
            "additional_notes": _("Дополнительные заметки"),
        }

    def clean_title(self):
        """Валидация названия проекта"""
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise forms.ValidationError(
                _("Название проекта должно содержать минимум 5 символов")
            )
        return title

    def clean_budget(self):
        """Валидация бюджета"""
        budget = self.cleaned_data.get("budget")
        if budget and budget < 0:
            raise forms.ValidationError(_("Бюджет не может быть отрицательным"))
        return budget


class OrderMessageForm(forms.ModelForm):
    """Форма сообщения в заказе"""

    class Meta:
        model = OrderMessage
        fields = ["message", "file"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите ваше сообщение...",
                    "rows": 4,
                }
            ),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "message": _("Сообщение"),
            "file": _("Прикрепить файл"),
        }


class ReviewForm(forms.ModelForm):
    """Форма отзыва"""

    class Meta:
        model = PortfolioReview  # Исправлено: PortfolioReview вместо Review
        fields = ["rating", "title", "content"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Заголовок отзыва"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Текст вашего отзыва...",
                    "rows": 6,
                }
            ),
        }
        labels = {
            "rating": _("Оценка"),
            "title": _("Заголовок отзыва"),
            "content": _("Текст отзыва"),
        }

    def clean_rating(self):
        """Валидация рейтинга"""
        rating = self.cleaned_data.get("rating")
        if rating not in [1, 2, 3, 4, 5]:
            raise forms.ValidationError(_("Пожалуйста, выберите корректную оценку"))
        return rating


class ClientProfileForm(forms.ModelForm):
    """Форма профиля клиента"""

    class Meta:
        model = Client
        fields = ["company", "phone", "website", "description"]
        widgets = {
            "company": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название компании"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 (999) 999-99-99"}
            ),
            "website": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://example.com"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Расскажите о себе или вашей компании...",
                    "rows": 5,
                }
            ),
        }
        labels = {
            "company": _("Компания"),
            "phone": _("Телефон"),
            "website": _("Веб-сайт"),
            "description": _("Описание"),
        }


class PortfolioSearchForm(forms.Form):
    """Форма поиска по портфолио"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по работам...",
                "aria-label": "Search",
            }
        ),
    )
    category = forms.ChoiceField(
        required=False, widget=forms.Select(attrs={"class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически заполняем категории
        from .models import PortfolioCategory

        categories = PortfolioCategory.objects.filter(is_active=True)
        choices = [("", "Все категории")] + [(cat.slug, cat.name) for cat in categories]
        self.fields["category"].choices = choices
