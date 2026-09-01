from django.conf import settings
from django.db import models


class JobView(models.Model):
    # Changed from 'jobs.Job' to 'accounts.Job'
    job = models.ForeignKey(
        "accounts.Job", on_delete=models.CASCADE, related_name="views"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProfileView(models.Model):
    profile = models.ForeignKey(
        "accounts.JobSeekerProfile",
        on_delete=models.CASCADE,
        related_name="profile_views",
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Placement(models.Model):
    # Changed from 'jobs.Application' to 'accounts.Application'
    application = models.OneToOneField(
        "accounts.Application", on_delete=models.CASCADE, related_name="placement"
    )
    hired_at = models.DateTimeField(auto_now_add=True)
    cost_per_hire = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class ResumeDownload(models.Model):
    job_seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resume_downloads",
    )
    downloaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="downloads_made",
    )
    created_at = models.DateTimeField(auto_now_add=True)
