from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    # 🛠️ Super Admin Dashboard
    path(
        "admin-dashboard/",
        views.super_admin_dashboard,
        name="super_admin_dashboard",
    ),
    # 📈 Employer / Recruitment Analytics
    path("employer/", views.employer_analytics, name="employer_analytics"),
    # 📊 Job Seeker Analytics
    path("job-seeker/", views.job_seeker_analytics, name="job_seeker_analytics"),
]
