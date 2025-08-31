from django import forms
from tinymce.widgets import TinyMCE
from .models import News, NewsCategory


class NewsCategoryForm(forms.ModelForm):
    class Meta:
        model = NewsCategory
        fields = "__all__"
        widgets = {
            "description": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = "__all__"
        widgets = {
            "content": TinyMCE(attrs={"cols": 80, "rows": 30}),
            "meta_description": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }
