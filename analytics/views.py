from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect
from django.utils import timezone

# Project Model Imports
from accounts.models import Application, Job
from ads.models import AdCampaign
from analytics.models import ResumeDownload
from billing.models import PaymentHistory

User = get_user_model()


# ==========================================
# 1. SUPER ADMIN DASHBOARD VIEW
# ==========================================
@staff_member_required
def super_admin_dashboard(request):
    now = timezone.now()

    # Core Counts
    total_users = User.objects.count()
    total_employers = (
        User.objects.filter(role="EMPLOYER").count()
        if hasattr(User, "role")
        else User.objects.filter(is_staff=True).count()
    )
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()

    # Subscription Revenue calculated from successful PaymentHistory entries
    sub_revenue = (
        PaymentHistory.objects.filter(status="success").aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )

    # Advertisement Revenue
    ad_revenue = 0
    try:
        ad_revenue = (
            AdCampaign.objects.aggregate(total=Sum("spent_amount"))["total"] or 0
        )
    except Exception:
        ad_revenue = 0

    total_revenue = sub_revenue + ad_revenue

    # Growth Trends (By Month)
    user_growth = (
        User.objects.annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    application_growth = (
        Application.objects.annotate(month=TruncMonth("applied_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    context = {
        "metrics": {
            "total_users": total_users,
            "total_employers": total_employers,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "total_revenue": total_revenue,
            "sub_revenue": sub_revenue,
            "ad_revenue": ad_revenue,
        },
        "user_growth": list(user_growth),
        "application_growth": list(application_growth),
    }

    return render(request, "analytics/super_admin_dashboard.html", context)


# ==========================================
# 2. EMPLOYER ANALYTICS VIEW
# ==========================================
@login_required
def employer_analytics(request):
    employer = request.user

    # FIXED: Use company__employer instead of direct employer field
    employer_jobs = Job.objects.filter(company__employer=employer)

    # Job Views & Applicants Count
    total_job_views = sum(
        job.views.count() if hasattr(job, "views") else 0 for job in employer_jobs
    )
    total_applicants = Application.objects.filter(
        job__company__employer=employer
    ).count()

    # Application Funnel
    funnel = Application.objects.filter(job__company__employer=employer).aggregate(
        applied=Count("id"),
        shortlisted=Count("id", filter=Q(status="SHORTLISTED")),
        interviewed=Count("id", filter=Q(status="INTERVIEWED")),
        hired=Count("id", filter=Q(status="HIRED")),
    )

    # Average Hiring Time (Days)
    hired_apps = Application.objects.filter(
        job__company__employer=employer, status="HIRED", placement__isnull=False
    )
    avg_hiring_days = None
    if hired_apps.exists():
        durations = [
            (app.placement.hired_at - app.applied_at).days for app in hired_apps
        ]
        avg_hiring_days = round(sum(durations) / len(durations), 1)

    context = {
        "total_job_views": total_job_views,
        "total_applicants": total_applicants,
        "funnel": funnel,
        "avg_hiring_days": avg_hiring_days or "N/A",
    }

    return render(request, "analytics/employer_analytics.html", context)


# ==========================================
# 3. JOB SEEKER ANALYTICS VIEW
# ==========================================
@login_required
def job_seeker_analytics(request):
    job_seeker = request.user

    # Application status counts
    applications = Application.objects.filter(applicant=job_seeker)

    # Proper integer count for resume downloads
    try:
        resume_downloads_count = ResumeDownload.objects.filter(
            job_seeker=job_seeker
        ).count()
    except Exception:
        resume_downloads_count = 0

    context = {
        "total_applications": applications.count(),
        "shortlisted_count": applications.filter(status="SHORTLISTED").count(),
        "interview_count": applications.filter(status="INTERVIEWED").count(),
        "hired_count": applications.filter(status="HIRED").count(),
        "resume_downloads": resume_downloads_count,
        "profile_views": getattr(job_seeker, "profile_views", 0),
    }

    return render(request, "analytics/job_seeker_analytics.html", context)
