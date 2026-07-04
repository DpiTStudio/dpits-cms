# accounts/forms_extra.py
# Дополнительные формы для приложения accounts (регистрация пароля, 2FA и т.д.)

from django import forms
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm, PasswordResetForm as DjangoPasswordResetForm
from django.core.exceptions import ValidationError
from .models import UserProfile
import pyotp
import re

# ---------------------------------------------------------------------------
# Форма запроса сброса пароля (ввод email)
# ---------------------------------------------------------------------------
class PasswordResetRequestForm(DjangoPasswordResetForm):
    """Форма, позволяющая пользователю запросить сброс пароля.

    Наследуемся от DjangoPasswordResetForm, чтобы воспользоваться готовой
    логикой отправки письма. Переопределяем только поля и их стили.
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
            "required": "Email обязателен",
            "invalid": "Введите корректный email",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем Bootstrap‑классы ко всем полям формы
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

# ---------------------------------------------------------------------------
# Форма установки нового пароля (по токену)
# ---------------------------------------------------------------------------
class SetPasswordForm(DjangoSetPasswordForm):
    """Форма установки нового пароля после подтверждения сброса.

    Добавляем стили Bootstrap и небольшую проверку сложности пароля.
    """

    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите новый пароль",
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Повторите пароль",
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )

    def clean_new_password1(self):
        pwd = self.cleaned_data.get("new_password1")
        # Минимальная длина 8 символов, минимум один символ цифра и буква
        if len(pwd) < 8:
            raise ValidationError("Пароль должен быть не короче 8 символов")
        if not re.search(r"[A-Za-z]", pwd) or not re.search(r"\d", pwd):
            raise ValidationError("Пароль должен содержать буквы и цифры")
        return pwd

# ---------------------------------------------------------------------------
# Форма настройки двухфакторной аутентификации (генерация TOTP‑секрета)
# ---------------------------------------------------------------------------
class TwoFactorSetupForm(forms.Form):
    """Форма, в которой пользователь подтверждает создание TOTP‑секрета.

    Пользователю отображается QR‑код, а он вводит код из приложения
    (Google Authenticator, Authy и пр.).
    """

    token = forms.CharField(
        label="Код из приложения",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123456"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        # Сохраняем TOTP‑секрет в профиль, если он еще не создан
        if not hasattr(self.user, "profile"):
            raise ValidationError("Профиль пользователя не найден")
        if not self.user.profile.totp_secret:
            # Генерируем новый секрет и сохраняем во временное поле
            self.user.profile.totp_secret = pyotp.random_base32()
            self.user.profile.save()

    def clean_token(self):
        token = self.cleaned_data.get("token")
        totp = pyotp.TOTP(self.user.profile.totp_secret)
        if not totp.verify(token, valid_window=1):
            raise ValidationError("Неверный код, проверьте приложение аутентификации")
        return token

# ---------------------------------------------------------------------------
# Форма подтверждения 2FA при входе (получение кода от пользователя)
# ---------------------------------------------------------------------------
class TwoFactorVerifyForm(forms.Form):
    """Форма для ввода одноразового кода при входе.

    Пользователь вводит текущий TOTP‑код, который проверяется в представлении.
    """
    token = forms.CharField(
        label="Код из приложения",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123456"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data.get("token")
        totp = pyotp.TOTP(self.user.profile.totp_secret)
        if not totp.verify(token, valid_window=1):
            raise ValidationError("Неверный код, попробуйте еще раз")
        return token
