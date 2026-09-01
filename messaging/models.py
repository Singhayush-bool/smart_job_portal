from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    job_seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="seeker_conversations"
    )
    recruiter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recruiter_conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job_seeker", "recruiter")

    def __str__(self):
        return f"Chat: {self.job_seeker.username} & {self.recruiter.username}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    attachment = models.FileField(upload_to="chat_attachments/", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
