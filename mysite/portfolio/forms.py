# portfolio/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, OrderMessage, Review, Client, PortfolioItem

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company = forms.CharField(max_length=200, required=False)
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаем профиль клиента
            Client.objects.create(
                user=user,
                company=self.cleaned_data.get('company', ''),
                phone=self.cleaned_data.get('phone', '')
            )
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'description', 'budget', 'deadline', 'requirements_file', 'additional_notes']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'additional_notes': forms.Textarea(attrs={'rows': 3}),
        }

class OrderMessageForm(forms.ModelForm):
    class Meta:
        model = OrderMessage
        fields = ['message', 'file']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['portfolio_item', 'rating', 'title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['company', 'phone', 'website', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'category', 'image', 'short_description', 'content', 
                 'technologies', 'project_date', 'project_url', 'github_url']
        widgets = {
            'project_date': forms.DateInput(attrs={'type': 'date'}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
        }