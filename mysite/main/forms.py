# forms.py
"""
ФОРМЫ ДЛЯ ПРИЛОЖЕНИЯ MAIN

Содержит формы обратной связи и другие публичные формы.
"""

from django import forms


class ContactForm(forms.Form):
    """
    Форма обратной связи на странице контактов.
    Поля: имя, email/телефон, сообщение.
    """

    name = forms.CharField(
        label="Ваше имя",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg bg-light border-0",
            "placeholder": "Как к вам обращаться?",
            "id": "contact_name",
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
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Имя должно содержать минимум 2 символа.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Сообщение должно содержать минимум 10 символов.")
        return message
