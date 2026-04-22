# services/forms.py
# Назначение: Формы для оформления заказа.
# Быстрый заказ (минимальные поля) и полный заказ (расширенный).

from django import forms
from django.utils.translation import gettext_lazy as _


class QuickOrderForm(forms.Form):
    """
    Форма быстрого заказа.
    Используется для минимального сбора информации от клиента.
    Доступна как авторизованным, так и неавторизованным пользователям.
    """
    client_name = forms.CharField(
        label="Ваше имя",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Иван Иванов",
            "autocomplete": "name",
        }),
        error_messages={"required": "Укажите ваше имя"},
    )
    client_email = forms.EmailField(
        label="Email",
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
        label="Телефон",
        max_length=30,
        required=False,  # Телефон необязателен в быстром заказе
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+7 (999) 123-45-67",
            "autocomplete": "tel",
        }),
    )
    comment = forms.CharField(
        label="Комментарий к заказу",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Дополнительные пожелания или уточнения…",
        }),
    )


class FullOrderForm(forms.Form):
    """
    Форма полного заказа.
    Собирает детальную информацию о проекте.
    """
    client_name = forms.CharField(
        label="Полное имя",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Иванов Иван Иванович",
            "autocomplete": "name",
        }),
        error_messages={"required": "Укажите ваше имя"},
    )
    client_email = forms.EmailField(
        label="Email для связи",
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
        label="Контактный телефон",
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+7 (999) 123-45-67",
            "autocomplete": "tel",
        }),
        error_messages={"required": "Телефон обязателен для полного заказа"},
    )
    comment = forms.CharField(
        label="Подробное описание задачи",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Опишите вашу задачу подробно: цели, сроки, бюджет, особые требования…",
        }),
        error_messages={"required": "Пожалуйста, опишите задачу"},
    )
    budget = forms.CharField(
        label="Ориентировочный бюджет",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "например: до 50 000 ₽ или договорная",
        }),
    )
    deadline = forms.CharField(
        label="Желаемые сроки",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "например: 2 недели или до 1 мая",
        }),
    )
    how_found = forms.ChoiceField(
        label="Как вы нас нашли?",
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