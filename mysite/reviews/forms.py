# reviews/forms.py

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["full_name", "phone", "email", "message"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше ФИО"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваш телефон"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Ваш email"}
            ),
            "message": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Ваш отзыв", "rows": 5}
            ),
        }
