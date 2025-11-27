from django import forms
from .models import Session, Profile, Review


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Don’t let them change role here – that’s done at signup
        fields = ["bio", "skills", "hourly_rate"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Tell others about your experience, interests, or goals."
            }),
            "skills": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Comma-separated skills (e.g. Python, Resume Review, Data Science)"
            }),
            "hourly_rate": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5,
                "placeholder": "Rate 1–5",
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your feedback about this session...",
            }),
        }
