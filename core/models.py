from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ("MENTOR", "Mentor"),
        ("MENTEE", "Mentee"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    skills = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated skills, e.g. Python, Data Science, Resume Review",
    )
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Only for mentors",
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Session(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    mentor = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="sessions_as_mentor",
    )
    mentee = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="sessions_as_mentee",
    )
    topic = models.CharField(max_length=200)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} - {self.mentor.user.username} with {self.mentee.user.username}"


class Review(models.Model):
    session = models.OneToOneField(
        Session,
        on_delete=models.CASCADE,
        related_name="review",
    )
    rating = models.PositiveSmallIntegerField()  # 1–5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.session} ({self.rating}/5)"


class Message(models.Model):
    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="messages_received",
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.user.username} to {self.recipient.user.username}"

# Automatically create Profile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically create a Profile whenever a new User is created.
    Default role = MENTEE (you can change this later).
    """
    if created:
        Profile.objects.create(user=instance, role="MENTEE")
#-------------------------ENDS HERE-------------------------------------------
