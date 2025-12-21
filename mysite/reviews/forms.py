from django import forms
from captcha.fields import CaptchaField
from .models import Review
import re


class ReviewForm(forms.ModelForm):
    captcha = CaptchaField(
        label="Защита от спама",
        error_messages={"invalid": "Неправильный код с картинки"},
    )

    class Meta:
        model = Review
        fields = ["full_name", "phone", "email", "message", "captcha"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше ФИО"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 (___) ___-__-__"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@mail.com"}
            ),
            "message": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Ваш отзыв", "rows": 5}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        # Простая проверка: должен содержать цифры и может начинаться с +
        if not re.match(r"^\+?[\d\s\-\(\)]+$", phone):
            raise forms.ValidationError(
                "Введите корректный номер телефона (цифры, пробелы, -, (, ), +)"
            )
        # Очистка от лишних символов для хранения (опционально, но оставим как есть)
        return phone
