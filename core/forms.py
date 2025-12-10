from django import forms
from .models import Session, Profile, Review, Availability, Message, Post, PostComment
from django.utils import timezone



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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # HTML-level restriction: can’t pick a time before now
        now = timezone.now()
        self.fields["scheduled_at"].widget.attrs["min"] = now.strftime("%Y-%m-%dT%H:%M")

    def clean_scheduled_at(self):
        dt = self.cleaned_data.get("scheduled_at")

        if not dt:
            return dt  # let required/blank validation handle empties

        if dt < timezone.now():
            raise forms.ValidationError("Please choose a date and time in the future.")

        return dt


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "skills", "hourly_rate", "photo"]  # ← include photo
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Tell others about yourself...",
                }
            ),
            "skills": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Data Structures, Python, Machine Learning",
                }
            ),
            "hourly_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            # photo uses default file input widget
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

class AvailabilityForm(forms.Form):
    """
    Let mentors select multiple days at once for the same time range.
    """
    day_of_week = forms.MultipleChoiceField(
        choices=Availability.DAY_OF_WEEK_CHOICES,  # uses the choices defined in the model
        widget=forms.CheckboxSelectMultiple,
        label="Days of the week",
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"type": "time", "class": "form-control"}
        ),
        label="Start time",
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"type": "time", "class": "form-control"}
        ),
        label="End time",
    )

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
    def clean_scheduled_at(self):
        dt = self.cleaned_data["scheduled_at"]
        if dt and dt < timezone.now():
            raise forms.ValidationError("Please choose a date and time in the future.")
        return dt
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Add a comment…",
                }
            )
        }
