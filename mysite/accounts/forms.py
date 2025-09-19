# accounts/forms.py

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from django.contrib.auth.models import User
from .models import UserProfile, Ticket, TicketResponse


class ProfileEditForm(UserChangeForm):
    password = None  # Убираем поле пароля

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя пользователя",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Введите email"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите фамилию"}
            ),
        }
        labels = {
            "username": "Имя пользователя",
            "email": "Email адрес",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Придумайте имя пользователя",
                }
            ),
        }
        labels = {
            "username": "Имя пользователя",
            "email": "Email адрес",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "avatar", "bio"]
        widgets = {
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 (XXX) XXX-XX-XX"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Расскажите о себе...",
                }
            ),
        }
        labels = {
            "phone": "Телефон",
            "avatar": "Аватар",
            "bio": "О себе",
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Краткое описание проблемы",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Подробно опишите вашу проблему...",
                }
            ),
        }
        labels = {
            "subject": "Тема тикета",
            "message": "Сообщение",
        }


class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Введите ваш ответ...",
                }
            ),
        }
        labels = {
            "message": "Сообщение",
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")
        widgets = {
            "old_password": forms.PasswordInput(),
            "new_password1": forms.PasswordInput(),
            "new_password2": forms.PasswordInput(),
        }
