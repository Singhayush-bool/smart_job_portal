from .models import Notification


def unread_notifications_count(request):
    """Logged-in user ke liye unread notifications ka count return karta hai."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {"unread_notifications_count": count}
    return {"unread_notifications_count": 0}
