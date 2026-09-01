import logging
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Corrected model import: Application instead of JobApplication
from .models import Application, JobSeekerProfile, User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# 1. Profile Creation Signal
# ---------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_job_seeker_profile(sender, instance, created, **kwargs):
    if created and instance.role == "job_seeker":
        JobSeekerProfile.objects.create(user=instance)


# ---------------------------------------------------------------------
# 2. Application Status Tracker (Pre-Save)
# ---------------------------------------------------------------------
@receiver(pre_save, sender=Application)
def track_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


# ---------------------------------------------------------------------
# 3. Application Email Alerts (Post-Save)
# ---------------------------------------------------------------------
@receiver(post_save, sender=Application)
def handle_application_email_notifications(sender, instance, created, **kwargs):
    try:
        from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL", "noreply@yourjobportal.com"
        )

        # Scenario A: New Application Created -> Notify Employer
        if created:
            employer = instance.job.company.employer
            employer_email = getattr(employer, "email", None)

            if employer_email:
                subject = f"🎯 New Application Received: {instance.job.title}"
                message = (
                    f"Hello {employer.get_full_name() or employer.username},\n\n"
                    f"A new candidate ({instance.applicant.get_full_name() or instance.applicant.username}) "
                    f"has just applied for '{instance.job.title}'.\n\n"
                    f"Log in to your Employer Dashboard to review their application.\n\n"
                    f"Best regards,\n"
                    f"Job Portal Team"
                )

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=[employer_email],
                    fail_silently=True,
                )

        # Scenario B: Status Updated -> Notify Candidate
        else:
            old_status = getattr(instance, "_old_status", None)
            current_status = instance.status

            if old_status and old_status != current_status:
                candidate = instance.applicant
                candidate_email = getattr(candidate, "email", None)

                if candidate_email:
                    status_display = (
                        instance.get_status_display()
                        if hasattr(instance, "get_status_display")
                        else current_status.title()
                    )

                    subject = f"📋 Application Status Update: {instance.job.title}"
                    message = (
                        f"Hello {candidate.get_full_name() or candidate.username},\n\n"
                        f"Your application status for '{instance.job.title}' at {instance.job.company.name} "
                        f"has been updated to: {status_display}.\n\n"
                        f"Best regards,\n"
                        f"{instance.job.company.name} Hiring Team"
                    )

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=[candidate_email],
                        fail_silently=True,
                    )

    except Exception as e:
        logger.error(
            f"Failed to send email notification for Application ID {instance.id}: {str(e)}"
        )
