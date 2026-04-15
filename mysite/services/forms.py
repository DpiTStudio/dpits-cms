# services/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _


class QuickOrderForm(forms.Form):
    """
    Быстрый заказ: минимальные поля — имя, email, телефон + необязательный комментарий.
    Доступен как гостям, так и авторизованным пользователям.
    """
    client_name = forms.CharField(
        label=_("Ваше имя"),
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Иван Иванов",
            "autocomplete": "name",
        }),
        error_messages={"required": "Укажите ваше имя"},
    )
    client_email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "example@mail.ru",
            "autocomplete": "email",
        }),
        error_messages={
            "required": "Email обязателен",
            "invalid": "Введите корректный email",
        },
    )
    client_phone = forms.CharField(
        label=_("Телефон"),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+7 (999) 123-45-67",
            "autocomplete": "tel",
        }),
    )
    comment = forms.CharField(
        label=_("Комментарий к заказу"),
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Дополнительные пожелания или уточнения…",
        }),
    )


class FullOrderForm(forms.Form):
    """
    Полный заказ: расширенная форма с деталями.
    """
    client_name = forms.CharField(
        label=_("Полное имя"),
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Иванов Иван Иванович",
            "autocomplete": "name",
        }),
        error_messages={"required": "Укажите ваше имя"},
    )
    client_email = forms.EmailField(
        label=_("Email для связи"),
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "example@mail.ru",
            "autocomplete": "email",
        }),
        error_messages={
            "required": "Email обязателен",
            "invalid": "Введите корректный email",
        },
    )
    client_phone = forms.CharField(
        label=_("Контактный телефон"),
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+7 (999) 123-45-67",
            "autocomplete": "tel",
        }),
        error_messages={"required": "Телефон обязателен для полного заказа"},
    )
    comment = forms.CharField(
        label=_("Подробное описание задачи"),
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Опишите вашу задачу подробно: цели, сроки, бюджет, особые требования…",
        }),
        error_messages={"required": "Пожалуйста, опишите задачу"},
    )
    budget = forms.CharField(
        label=_("Ориентировочный бюджет"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "например: до 50 000 ₽ или договорная",
        }),
    )
    deadline = forms.CharField(
        label=_("Желаемые сроки"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "например: 2 недели или до 1 мая",
        }),
    )
    how_found = forms.ChoiceField(
        label=_("Как вы нас нашли?"),
        required=False,
        choices=[
            ("", "— не указано —"),
            ("search", "Поисковая система"),
            ("social", "Социальные сети"),
            ("recommendation", "Рекомендация"),
            ("repeat", "Повторный клиент"),
            ("other", "Другое"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
