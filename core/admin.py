from django.contrib import admin
from .models import Profile, Session, Message, Review, Skill

admin.site.register(Skill)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "skills", "hourly_rate")
    list_filter = ("role",)
    search_fields = ("user__username", "skills", "bio")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("topic", "mentor", "mentee", "status", "scheduled_at")
    list_filter = ("status",)
    search_fields = ("topic", "mentor__user__username", "mentee__user__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "sent_at", "is_read")
    list_filter = ("is_read",)
    search_fields = (
        "sender__user__username",
        "recipient__user__username",
        "content",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("session", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("session__mentor__user__username",)
