import uuid
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class TicketCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class SupportTicket(models.Model):
    PRIORITY_CHOICES = (
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    )

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    )

    ticket_id = models.CharField(
        max_length=20, unique=True, editable=False, default=uuid.uuid4
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="OPEN")

    # Admin Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.ticket_id[:8]} - {self.subject}"


class TicketReply(models.Model):
    ticket = models.ForeignKey(
        SupportTicket, on_delete=models.CASCADE, related_name="replies"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(
        upload_to="ticket_attachments/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
