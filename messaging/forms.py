from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text", "attachment"]
        widgets = {
            "text": forms.TextInput(
                attrs={
                    "class": "form-control border-0 bg-light py-2 px-3",
                    "placeholder": "Write a message...",
                    "autocomplete": "off",
                    "style": "border-radius: 20px;",
                }
            ),
            "attachment": forms.ClearableFileInput(
                attrs={"class": "form-control form-control-sm"}
            ),
        }
