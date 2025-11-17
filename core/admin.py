from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, Session, Review, Message


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "hourly_rate")
    list_filter = ("role",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("topic", "mentor", "mentee", "scheduled_at", "status")
    list_filter = ("status", "scheduled_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("session", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "sent_at", "is_read")
    list_filter = ("is_read", "sent_at")
