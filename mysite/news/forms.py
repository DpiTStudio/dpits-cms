from django import forms
from .models import Comment
from captcha.fields import CaptchaField


class CommentForm(forms.ModelForm):
    captcha = CaptchaField(label="Защита от спама", required=False)

    class Meta:
        model = Comment
        fields = ["name", "email", "content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control news-comment-textarea",
                    "placeholder": "Напишите ваш комментарий здесь...",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control news-comment-input",
                    "placeholder": "Ваше имя",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control news-comment-input",
                    "placeholder": "Ваш e-mail",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Если пользователь авторизован, скрываем контактные поля и капчу
        if self.user and self.user.is_authenticated:
            self.fields.pop("name")
            self.fields.pop("email")
            self.fields.pop("captcha")
        else:
            # Для гостей имя, почта и капча обязательны
            self.fields["name"].required = True
            self.fields["email"].required = True
            self.fields["captcha"].required = True
            # Сделаем саму капчу обязательным полем
            self.fields["captcha"].widget.attrs.update(
                {"placeholder": "Введите символы с картинки"}
            )
