# accounts/forms.py
# Формы для работы с данными пользователей и системой тикетов

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    AuthenticationForm,
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import UserProfile, Ticket, TicketResponse
from captcha.fields import CaptchaField


class UserRegisterForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.
    Включает email, username, два пароля и проверку капчей.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите ваш email",
                "autocomplete": "email",
            }
        ),
        error_messages={
            "required": "Email обязателен для заполнения",
            "invalid": "Введите корректный email адрес",
        },
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Придумайте имя пользователя",
                "autocomplete": "username",
            }
        ),
        help_text="Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_.",
        error_messages={
            "required": "Имя пользователя обязательно",
            "unique": "Пользователь с таким именем уже существует",
        },
    )

    # Поле капчи для защиты от автоматических регистраций
    captcha = CaptchaField(
        error_messages={
            "invalid": "Неверно введена капча. Попробуйте еще раз.",
            "required": "Подтвердите, что вы не робот.",
        }
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "password1": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите пароль",
                    "autocomplete": "new-password",
                }
            ),
            "password2": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Повторите пароль",
                    "autocomplete": "new-password",
                }
            ),
        }
        labels = {
            "username": "Имя пользователя",
            "email": "Email адрес",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }

    def clean_email(self):
        """Проверка уникальности email адреса"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

    def clean_username(self):
        """Дополнительная валидация длины имени пользователя"""
        username = self.cleaned_data.get("username")
        if len(username) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
        return username


class CustomAuthenticationForm(AuthenticationForm):
    """
    Кастомная форма входа с добавлением поля капчи.
    """

    captcha = CaptchaField(
        error_messages={
            "invalid": "Неверно введена капча. Попробуйте еще раз.",
            "required": "Подтвердите, что вы не робот.",
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка Bootstrap-классов для стандартных полей Django
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите имя пользователя или email",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите ваш пароль",
                "autocomplete": "current-password",
            }
        )
        self.fields["captcha"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Введите символы с картинки",
            }
        )


class UserUpdateForm(forms.ModelForm):
    """
    Форма для обновления основных данных пользователя (имя, фамилия, почта).
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите email"}
        ),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите фамилию"}
            ),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Форма для обновления профиля (расширенная информация).
    """

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
            "avatar": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
        labels = {
            "phone": "Телефон",
            "avatar": "Аватар",
            "bio": "О себе",
        }

    def clean_phone(self):
        """Валидация формата номера телефона с помощью регулярного выражения"""
        phone = self.cleaned_data.get("phone")
        if phone:
            phone_regex = r"^\+?[1-9]\d{1,14}$"
            if not re.match(
                phone_regex,
                phone.replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", ""),
            ):
                raise ValidationError("Введите корректный номер телефона")
        return phone


class TicketForm(forms.ModelForm):
    """
    Форма создания нового тикета в службу поддержки.
    """

    class Meta:
        model = Ticket
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Кратко опишите суть обращения",
                    "maxlength": "200",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Опишите вашу проблему или вопрос максимально подробно...",
                    "minlength": "10",
                }
            ),
        }
        labels = {
            "subject": "Тема обращения",
            "message": "Суть проблемы",
        }

    def clean_subject(self):
        """Проверка минимальной длины темы"""
        subject = self.cleaned_data.get("subject")
        if len(subject.strip()) < 5:
            raise ValidationError("Тема должна содержать минимум 5 символов")
        return subject

    def clean_message(self):
        """Проверка минимальной длины текста сообщения"""
        message = self.cleaned_data.get("message")
        if len(message.strip()) < 10:
            raise ValidationError("Сообщение должно содержать минимум 10 символов")
        return message


class TicketResponseForm(forms.ModelForm):
    """
    Форма для добавления ответа в существующий тикет.
    """

    class Meta:
        model = TicketResponse
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Напишите ваш ответ администрации...",
                    "minlength": "2",
                }
            ),
        }
        labels = {
            "message": "Ваш ответ",
        }

    def clean_message(self):
        """Проверка, что ответ не слишком короткий"""
        message = self.cleaned_data.get("message")
        if len(message.strip()) < 2:
            raise ValidationError("Ответ должен содержать хотя бы 2 символа")
        return message


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Кастомная форма смены пароля с Bootstrap стилями.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "autocomplete": "current-password"
                    if field_name == "old_password"
                    else "new-password",
                }
            )
            if field_name == "old_password":
                field.widget.attrs["placeholder"] = "Введите имеющийся пароль"
            elif field_name == "new_password1":
                field.widget.attrs["placeholder"] = "Придумайте новый сложный пароль"
            elif field_name == "new_password2":
                field.widget.attrs["placeholder"] = "Введите новый пароль еще раз"


class ProfileEditForm(forms.ModelForm):
    """
    Форма редактирования данных профиля (аналог UserUpdateForm для определенных страниц).
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Ваш email"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Желаемое имя пользователя",
                }
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваша фамилия"}
            ),
        }
        labels = {
            "username": "Логин",
            "email": "Электронная почта",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
