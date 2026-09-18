from django.contrib.auth import views as auth_views
from django.urls import path
from notifications import views as notification_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Auth & Email OTP Verification
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path(
        "verify-otp/", views.verify_otp, name="verify_otp"
    ),  # <--- Naya OTP verification route
    # Password Reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            success_url="/accounts/password-reset/done/",
            email_template_name="accounts/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<str:uidb64>/<str:token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/password-reset-complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Dashboards
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "job-seeker/dashboard/",
        views.job_seeker_dashboard,
        name="job_seeker_dashboard",
    ),
    path(
        "employer/dashboard/",
        views.employer_dashboard,
        name="employer_dashboard",
    ),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # Profile & Details
    path("profile/", views.profile, name="profile"),
    path("profile/education/add/", views.add_education, name="add_education"),
    path(
        "profile/education/<int:education_id>/edit/",
        views.edit_education,
        name="edit_education",
    ),
    path(
        "profile/education/<int:education_id>/delete/",
        views.delete_education,
        name="delete_education",
    ),
    path("profile/experience/add/", views.add_experience, name="add_experience"),
    path(
        "profile/experience/<int:experience_id>/edit/",
        views.edit_experience,
        name="edit_experience",
    ),
    path(
        "profile/experience/<int:experience_id>/delete/",
        views.delete_experience,
        name="delete_experience",
    ),
    path("profile/skills/add/", views.add_skill, name="add_skill"),
    path(
        "profile/skills/remove/<int:skill_id>/",
        views.remove_skill,
        name="remove_skill",
    ),
    # Resumes
    path("profile/resumes/", views.resume_list, name="resume_list"),
    path("profile/resume/upload/", views.upload_resume, name="upload_resume"),
    path(
        "profile/resumes/<int:resume_id>/default/",
        views.set_default_resume,
        name="set_default_resume",
    ),
    path(
        "profile/resumes/<int:resume_id>/delete/",
        views.delete_resume,
        name="delete_resume",
    ),
    path(
        "profile/resumes/<int:resume_id>/download/",
        views.download_resume,
        name="download_resume",
    ),
    # Company & Employer Jobs
    path("company/create/", views.create_company, name="create_company"),
    path("company/", views.employer_company, name="employer_company"),
    path("jobs/create/", views.create_job, name="create_job"),
    path("employer/jobs/", views.employer_jobs, name="employer_jobs"),
    path(
        "employer/jobs/<int:job_id>/toggle/",
        views.toggle_job_status,
        name="toggle_job_status",
    ),
    path(
        "employer/jobs/<int:job_id>/applicants/",
        views.job_applicants,
        name="job_applicants",
    ),
    path(
        "employer/applications/<int:application_id>/status/",
        views.update_application_status,
        name="update_application_status",
    ),
    # Admin Job Approval
    path("portal-admin/jobs/", views.admin_jobs, name="admin_jobs"),
    path(
        "portal-admin/jobs/<int:job_id>/approve/",
        views.approve_job,
        name="approve_job",
    ),
    # Job Seekers & Applications
    path("jobs/list/", views.job_list, name="job_list"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/save/", views.save_job, name="save_job"),
    path("jobs/<int:job_id>/unsave/", views.unsave_job, name="unsave_job"),
    path("saved-jobs/", views.saved_jobs, name="saved_jobs"),
    path("jobs/<int:job_id>/apply/", views.apply_job, name="apply_job"),
    path("my-applications/", views.my_applications, name="my_applications"),
    # Social Posts & Feed
    path("feed/", views.feed, name="feed"),
    path("post/create/", views.create_post, name="create_post"),
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/reply/", views.add_reply, name="add_reply"),
    path(
        "comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path(
        "post/<int:post_id>/repost/",
        views.toggle_repost,
        name="toggle_repost",
    ),
    path(
        "post/<int:post_id>/save/",
        views.toggle_save_post,
        name="toggle_save_post",
    ),
    # Social Network & Connections
    path("people/", views.people, name="people"),
    path("profile/user/<int:user_id>/", views.user_profile, name="user_profile"),
    path(
        "profile/user/<int:user_id>/follow/",
        views.toggle_follow,
        name="toggle_follow",
    ),
    path(
        "profile/user/<int:user_id>/connect/",
        views.send_connection,
        name="send_connection",
    ),
    path(
        "connection/<int:connection_id>/accept/",
        views.accept_connection,
        name="accept_connection",
    ),
    path(
        "connection/<int:connection_id>/reject/",
        views.reject_connection,
        name="reject_connection",
    ),
    path(
        "notifications/read/<int:notif_id>/",
        notification_views.mark_as_read,
        name="mark_notification_read",
    ),
    path(
        "profile/certifications/add/",
        views.add_certification,
        name="add_certification",
    ),
    path("post/<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("job/edit/<int:pk>/", views.edit_job, name="edit_job"),
    path("job/delete/<int:pk>/", views.delete_job, name="delete_job"),
    path("search/", views.global_search, name="global_search"),
    path("saved-posts/", views.saved_posts_list, name="saved_posts_list"),
    path(
        "jobs/<int:job_id>/generate-cover-letter/",
        views.generate_ai_cover_letter,
        name="generate_ai_cover_letter",
    ),
]
