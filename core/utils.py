from .models import Notification

def notify(recipient_profile, title, message, link=""):
    Notification.objects.create(
        recipient=recipient_profile,
        title=title,
        message=message,
        link=link,
    )
