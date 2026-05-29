# forms.py
"""
ФОРМЫ ДЛЯ ПРИЛОЖЕНИЯ MAIN

Содержит формы обратной связи и другие публичные формы.
"""

import re
from django import forms


class ContactForm(forms.Form):
    """
    Форма обратной связи на странице контактов.
    Поля: имя, email/телефон, сообщение.

    Включает:
    - Валидацию длины имени (минимум 2 символа)
    - Валидацию формата email или номера телефона
    - Валидацию длины сообщения (минимум 10 символов)
    """

    # Email-паттерн: стандартный формат user@domain.tld
    EMAIL_RE = re.compile(r'^[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}$')
    # Телефонный паттерн: +7 (900) 000-00-00, 8 900 0000000 и т.д.
    PHONE_RE = re.compile(r'^[\+\d][\d\s\-\(\)]{6,19}$')

    name = forms.CharField(
        label="Ваше имя",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg bg-light border-0",
            "placeholder": "Как к вам обращаться?",
            "id": "contact_name",
            "autocomplete": "name",
        }),
        error_messages={"required": "Пожалуйста, укажите ваше имя."},
    )

    contact = forms.CharField(
        label="Email или Телефон",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg bg-light border-0",
            "placeholder": "Для связи с вами",
            "id": "contact_contact",
            "autocomplete": "email",
        }),
        error_messages={"required": "Укажите email или телефон для обратной связи."},
    )

    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            "class": "form-control form-control-lg bg-light border-0",
            "placeholder": "Напишите ваш вопрос...",
            "rows": 4,
            "id": "contact_message",
        }),
        error_messages={"required": "Пожалуйста, напишите сообщение."},
    )

    def clean_name(self):
        """Проверяет, что имя содержит минимум 2 символа."""
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Имя должно содержать минимум 2 символа.")
        return name

    def clean_contact(self):
        """
        Валидирует поле contact: принимает корректный email или номер телефона.
        Предотвращает ввод случайных строк и пустых значений.
        """
        contact = self.cleaned_data.get("contact", "").strip()

        if not self.EMAIL_RE.match(contact) and not self.PHONE_RE.match(contact):
            raise forms.ValidationError(
                "Введите корректный email (example@mail.com) "
                "или номер телефона (+7 900 000-00-00)."
            )
        return contact

    def clean_message(self):
        """Проверяет, что сообщение содержит минимум 10 символов."""
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Сообщение должно содержать минимум 10 символов.")
        return message
