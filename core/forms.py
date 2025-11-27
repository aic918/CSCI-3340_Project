from django import forms
from .models import Session


class SessionRequestForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["topic", "scheduled_at"]
        widgets = {
            "topic": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "What do you want help with? (e.g., Resume review, Python basics)"
            }),
            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }
