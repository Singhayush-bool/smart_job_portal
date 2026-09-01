# cms/forms.py
from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "category", "featured_image", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "What do you want to share or discuss?",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your article or career tip here...",
                }
            ),
        }
