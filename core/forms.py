from django import forms
from .models import Session, Profile, Review, Availability, Message


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
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
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

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ["day_of_week", "start_time", "end_time"]
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "form-select"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write a message..."
            }),
        }

class RescheduleForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["scheduled_at"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            )
        }
