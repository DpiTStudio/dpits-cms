# feedback/forms.py
# Формы для приложения feedback (обратная связь)

from django import forms  # Импорт базовых классов форм Django
from captcha.fields import CaptchaField  # Импорт поля капчи
from .models import FeedbackMessage  # Импорт модели сообщения обратной связи


class FeedbackForm(forms.ModelForm):
    """
    Форма для создания сообщения обратной связи.
    Включает капчу для защиты от спама.
    """
    
    captcha = CaptchaField(
        label="Капча",  # Метка поля капчи
        help_text="Введите символы с изображения",  # Подсказка для пользователя
    )
    
    class Meta:
        """Метаданные формы."""
        model = FeedbackMessage  # Модель, с которой связана форма
        fields = ["subject", "message", "email"]  # Поля формы
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",  # CSS класс для стилизации
                    "placeholder": "Тема сообщения",  # Подсказка в поле
                    "required": True,  # Поле обязательно для заполнения
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",  # CSS класс для стилизации
                    "placeholder": "Ваше сообщение...",  # Подсказка в поле
                    "rows": 8,  # Количество строк текстового поля
                    "required": True,  # Поле обязательно для заполнения
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",  # CSS класс для стилизации
                    "placeholder": "your@email.com",  # Подсказка в поле
                    "required": True,  # Поле обязательно для заполнения
                }
            ),
        }
        labels = {
            "subject": "Тема",  # Метка поля темы
            "message": "Сообщение",  # Метка поля сообщения
            "email": "Email для ответа",  # Метка поля email
        }
        help_texts = {
            "subject": "Кратко опишите суть вашего вопроса или сообщения",  # Подсказка для поля темы
            "message": "Подробно опишите ваш вопрос, предложение или проблему",  # Подсказка для поля сообщения
            "email": "На этот адрес будет отправлен ответ от администрации",  # Подсказка для поля email
        }
    
    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        Устанавливает начальные значения полей для зарегистрированных пользователей.
        
        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы (может содержать user)
        """
        self.user = kwargs.pop("user", None)  # Извлекаем пользователя из аргументов
        super().__init__(*args, **kwargs)  # Вызываем инициализацию родительского класса
        
        # Если пользователь зарегистрирован, заполняем email автоматически
        if self.user and self.user.is_authenticated:  # Проверяем, аутентифицирован ли пользователь
            if self.user.email:  # Если у пользователя есть email
                self.fields["email"].initial = self.user.email  # Устанавливаем email пользователя по умолчанию
    
    def clean_message(self):
        """
        Валидация поля сообщения.
        Проверяет, что сообщение не пустое и имеет достаточную длину.
        
        Returns:
            str: Очищенное значение сообщения
            
        Raises:
            forms.ValidationError: Если сообщение пустое или слишком короткое
        """
        message = self.cleaned_data.get("message", "")  # Получаем значение сообщения
        
        if not message or not message.strip():  # Проверяем, что сообщение не пустое
            raise forms.ValidationError("Сообщение не может быть пустым")  # Вызываем ошибку валидации
        
        if len(message.strip()) < 10:  # Проверяем минимальную длину сообщения
            raise forms.ValidationError("Сообщение должно содержать минимум 10 символов")  # Вызываем ошибку валидации
        
        return message  # Возвращаем очищенное значение
    
    def clean_subject(self):
        """
        Валидация поля темы.
        Проверяет, что тема не пустая и имеет достаточную длину.
        
        Returns:
            str: Очищенное значение темы
            
        Raises:
            forms.ValidationError: Если тема пустая или слишком короткая
        """
        subject = self.cleaned_data.get("subject", "")  # Получаем значение темы
        
        if not subject or not subject.strip():  # Проверяем, что тема не пустая
            raise forms.ValidationError("Тема не может быть пустой")  # Вызываем ошибку валидации
        
        if len(subject.strip()) < 3:  # Проверяем минимальную длину темы
            raise forms.ValidationError("Тема должна содержать минимум 3 символа")  # Вызываем ошибку валидации
        
        return subject  # Возвращаем очищенное значение

