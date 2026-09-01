from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q
from .models import Notification
from accounts.models import Connection


@login_required
def notification_list(request):
    """Logged-in user ki saari notifications fetch karta hai aur connection status check karta hai."""
    notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    # Har notification ke liye connection status check karke attach karein
    for notif in notifications:
        notif.connection_status = None
        if notif.sender and (
            "connection" in notif.title.lower() or "request" in notif.title.lower()
        ):
            conn = Connection.objects.filter(
                Q(sender=request.user, receiver=notif.sender)
                | Q(sender=notif.sender, receiver=request.user)
            ).first()
            if conn:
                notif.connection_status = conn.status  # 'pending' ya 'accepted'
            else:
                notif.connection_status = "none"

    unread_count = notifications.filter(is_read=False).count()
    return render(
        request,
        "notifications/notification_list.html",
        {"notifications": notifications, "unread_count": unread_count},
    )


@login_required
def mark_as_read(request, pk):
    """Single notification ko read mark karta hai."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect("notifications:notification_list")


@login_required
def mark_all_as_read(request):
    """User ki saari unread notifications ko ek sath read mark karta hai."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:notification_list")


@login_required
def accept_connection_notification(request, pk):
    """Connection accept karta hai aur user ke profile page par bhejta hai."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    sender_user = notification.sender

    notification.is_read = True
    notification.save()

    if sender_user:
        # Pending connection ko accept karein
        Connection.objects.filter(
            sender=sender_user, receiver=request.user, status="pending"
        ).update(status="accepted")

        # Dono taraf se connection relationship ensure karne ke liye
        Connection.objects.get_or_create(
            sender=request.user, receiver=sender_user, defaults={"status": "accepted"}
        )

        messages.success(request, f"You are now connected with {sender_user.username}!")
        return redirect("accounts:user_profile", user_id=sender_user.id)

    return redirect("notifications:notification_list")


@login_required
def reject_connection_notification(request, pk):
    """Connection request ko reject/delete karta hai."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    sender_user = notification.sender

    notification.is_read = True
    notification.save()

    if sender_user:
        Connection.objects.filter(
            sender=sender_user, receiver=request.user, status="pending"
        ).delete()
        messages.info(request, "Connection request ignored.")

    return redirect("notifications:notification_list")


from django.contrib.auth.views import PasswordResetCompleteView
from notifications.models import Notification  # Aapke notification model ke mutabiq


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *kwargs):
        # Yahan aap check kar sakte hain ya notification bhej sakte hain
        # Lekin kyunki user logged out hai, hum session ya user object ke through handle karte hain
        response = super().get(request, *kwargs)
        return response
