from django import forms
from .models import SupportTicket, TicketReply


class TicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["category", "subject", "description", "priority"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
        }


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ["message", "attachment"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write your reply...",
                }
            ),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
