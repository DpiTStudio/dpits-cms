# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import (
    UserProfile,
    Ticket,
    TicketResponse,
)  # Добавьте TicketResponse в импорт


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "avatar", "bio"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse  # Теперь эта модель будет доступна
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
