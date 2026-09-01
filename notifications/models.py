from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    CHANNEL_CHOICES = (
        ("IN_APP", "In-App"),
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
        ("WHATSAPP", "WhatsApp"),
        ("PUSH", "Push Notification"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_notifications"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_notifs",
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    channel = models.CharField(max_length=15, choices=CHANNEL_CHOICES, default="IN_APP")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title or self.message[:30]}"
