from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

import random
from django.utils import timezone
from django.core.mail import send_mail

from .decorators import role_required

# Billing models import for subscription guard & usage tracking
from billing.models import Subscription, SubscriptionUsage

# 🟢 Notifications app se model import karein
from notifications.models import Notification

from .forms import (
    RegisterForm,
    JobSeekerProfileForm,
    EducationForm,
    ExperienceForm,
    JobSeekerSkillForm,
    ResumeForm,
    CompanyForm,
    JobForm,
    PostForm,
    CertificationForm,
)

from .models import (
    User,
    JobSeekerProfile,
    JobSeekerSkill,
    Education,
    Experience,
    Resume,
    JobCategory,
    Industry,
    Company,
    Job,
    SavedJob,
    Application,
    Post,
    PostLike,
    PostComment,
    Repost,
    SavedPost,
    Follow,
    Connection,
    # Notification, # <--- Accounts model se hata diya hai taaki conflict na ho
)

from cms.utils import generate_job_posting_schema
from messaging.models import Conversation, Message

# =========================================================
# HOME & MAIN DASHBOARD (UNIFIED)
# =========================================================


@login_required
def home(request):
    connection_requests = Connection.objects.filter(
        receiver=request.user, status="pending"
    ).count()

    people = User.objects.exclude(id=request.user.id).order_by("username")[:5]

    return render(
        request,
        "accounts/home.html",
        {
            "connection_requests": connection_requests,
            "people": people,
        },
    )


@login_required
def dashboard(request):
    """
    Renders the central unified role-based dashboard for all users,
    including posts feed and real-time messaging stats.
    """
    user = request.user

    posts = (
        Post.objects.filter(is_active=True)
        .select_related("author")
        .prefetch_related("likes", "comments", "reposted_by")
        .order_by("-created_at")
    )

    unread_count = Message.objects.filter(
        (Q(conversation__job_seeker=user) | Q(conversation__recruiter=user))
        & ~Q(sender=user)
        & Q(is_read=False)
    ).count()

    recent_conversations = Conversation.objects.filter(
        Q(job_seeker=user) | Q(recruiter=user)
    ).order_by("-updated_at")[:5]

    context = {
        "posts": posts,
        "unread_count": unread_count,
        "recent_conversations": recent_conversations,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context,
    )


# =========================================================
# REGISTER & EMAIL OTP VERIFICATION
# =========================================================


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False

            # 6-digit random OTP generate karein
            otp = str(random.randint(100000, 999999))
            user.email_otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            subject = "Your SmartJobs Account Verification OTP"
            message = (
                f"Hi {user.username},\n\n"
                f"Thank you for registering with SmartJobs. Your 6-digit email verification OTP is: {otp}\n\n"
                "This OTP is valid for account activation. If you did not request this, please ignore this email."
            )

            try:
                send_mail(
                    subject,
                    message,
                    None,
                    [user.email],
                    fail_silently=False,
                )
                request.session["verify_user_id"] = user.pk
                messages.success(
                    request,
                    "Registration successful! Please enter the 6-digit OTP sent to your email.",
                )
                return redirect("accounts:verify_otp")
            except Exception as e:
                messages.warning(
                    request,
                    "Registration successful, but failed to send verification email.",
                )
                return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def verify_otp(request):
    user_id = request.session.get("verify_user_id")
    if not user_id:
        messages.error(
            request, "Session expired or invalid access. Please register again."
        )
        return redirect("accounts:register")

    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()

        if user.email_otp and user.email_otp == entered_otp:
            user.is_verified = True
            user.email_otp = None
            user.otp_created_at = None
            user.save()

            del request.session["verify_user_id"]

            messages.success(request, "Email verified successfully! You can now login.")
            return redirect("accounts:login")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "accounts/verify_otp.html", {"email": user.email})


# =========================================================
# LOGIN & LOGOUT
# =========================================================


def user_login(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if hasattr(user, "is_verified") and not user.is_verified:
                messages.error(request, "Please verify your email first.")
                return render(request, "accounts/login.html")

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("accounts:dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("accounts:login")


# =========================================================
# DASHBOARDS BY ROLE
# =========================================================


@login_required
@role_required("job_seeker")
def job_seeker_dashboard(request):
    return render(request, "accounts/job_seeker_dashboard.html")


@login_required
@role_required("employer")
def employer_dashboard(request):
    return render(request, "accounts/employer_dashboard.html")


@login_required
@role_required("admin")
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")


# =========================================================
# USER PROFILE
# =========================================================


@login_required
def profile(request):
    user = request.user
    profile_obj, created = JobSeekerProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()

        if request.FILES.get("profile_image"):
            profile_obj.profile_image = request.FILES["profile_image"]

        if getattr(user, "role", "") == "employer":
            if hasattr(profile_obj, "company_name"):
                profile_obj.company_name = request.POST.get(
                    "company_name", getattr(profile_obj, "company_name", "")
                )
            if hasattr(profile_obj, "website_url"):
                profile_obj.website_url = request.POST.get(
                    "website_url", getattr(profile_obj, "website_url", "")
                )

        profile_obj.location = request.POST.get(
            "location", getattr(profile_obj, "location", "")
        )
        profile_obj.bio = request.POST.get("bio", getattr(profile_obj, "bio", ""))
        profile_obj.linkedin_url = request.POST.get(
            "linkedin_url", getattr(profile_obj, "linkedin_url", "")
        )
        profile_obj.github_url = request.POST.get(
            "github_url", getattr(profile_obj, "github_url", "")
        )
        profile_obj.portfolio_url = request.POST.get(
            "portfolio_url", getattr(profile_obj, "portfolio_url", "")
        )
        profile_obj.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    fields_to_check = [
        user.first_name,
        user.last_name,
        profile_obj.location,
        profile_obj.bio,
        profile_obj.profile_image,
    ]
    filled = sum(1 for item in fields_to_check if item)
    completion = int((filled / len(fields_to_check)) * 100) if fields_to_check else 0

    followers = [
        f.follower
        for f in Follow.objects.filter(following=user).select_related("follower")
    ]
    following_users = [
        f.following
        for f in Follow.objects.filter(follower=user).select_related("following")
    ]

    sent_conns = Connection.objects.filter(sender=user, status="accepted")
    recv_conns = Connection.objects.filter(receiver=user, status="accepted")
    connections = [
        c.receiver if c.sender == user else c.sender
        for c in (list(sent_conns) + list(recv_conns))
    ]

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile_obj,
            "completion": completion,
            "followers": followers,
            "following_users": following_users,
            "connections": connections,
            "followers_count": len(followers),
            "following_count": len(following_users),
        },
    )


# =========================================================
# EDUCATION & EXPERIENCE
# =========================================================


@login_required
@role_required("job_seeker")
def add_education(request):
    profile_obj, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = profile_obj
            education.save()
            messages.success(request, "Education added successfully!")
            return redirect("accounts:profile")
    else:
        form = EducationForm()
    return render(request, "accounts/add_education.html", {"form": form})


@login_required
@role_required("job_seeker")
def edit_education(request, education_id):
    education = get_object_or_404(
        Education, id=education_id, profile=request.user.job_seeker_profile
    )
    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Education updated successfully!")
            return redirect("accounts:profile")
    else:
        form = EducationForm(instance=education)
    return render(request, "accounts/add_education.html", {"form": form, "edit": True})


@login_required
@role_required("job_seeker")
def delete_education(request, education_id):
    education = get_object_or_404(
        Education, id=education_id, profile=request.user.job_seeker_profile
    )
    education.delete()
    messages.success(request, "Education deleted successfully!")
    return redirect("accounts:profile")


@login_required
@role_required("job_seeker")
def add_experience(request):
    profile_obj, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.profile = profile_obj
            experience.save()
            messages.success(request, "Experience added successfully!")
            return redirect("accounts:profile")
    else:
        form = ExperienceForm()
    return render(request, "accounts/add_experience.html", {"form": form})


@login_required
@role_required("job_seeker")
def edit_experience(request, experience_id):
    experience = get_object_or_404(
        Experience, id=experience_id, profile=request.user.job_seeker_profile
    )
    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Experience updated successfully!")
            return redirect("accounts:profile")
    else:
        form = ExperienceForm(instance=experience)
    return render(request, "accounts/add_experience.html", {"form": form, "edit": True})


@login_required
@role_required("job_seeker")
def delete_experience(request, experience_id):
    experience = get_object_or_404(
        Experience, id=experience_id, profile=request.user.job_seeker_profile
    )
    experience.delete()
    messages.success(request, "Experience deleted successfully!")
    return redirect("accounts:profile")


# =========================================================
# SKILLS & CERTIFICATIONS
# =========================================================


@login_required
@role_required("job_seeker")
def add_skill(request):
    profile_obj, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = JobSeekerSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.profile = profile_obj
            skill.save()
            messages.success(request, "Skill added successfully!")
            return redirect("accounts:profile")
    else:
        form = JobSeekerSkillForm()
    return render(request, "accounts/add_skill.html", {"form": form})


@login_required
def add_certification(request):
    profile_obj, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.profile = profile_obj
            cert.save()
            messages.success(request, "Certification added successfully!")
            return redirect("accounts:profile")
    else:
        form = CertificationForm()
    return render(request, "accounts/add_certification.html", {"form": form})


@login_required
@role_required("job_seeker")
def remove_skill(request, skill_id):
    profile_obj = request.user.job_seeker_profile
    skill = get_object_or_404(JobSeekerSkill, id=skill_id, profile=profile_obj)
    skill.delete()
    messages.success(request, "Skill removed successfully!")
    return redirect("accounts:profile")


# =========================================================
# RESUME & BILLING RESUME DOWNLOAD INTEGRATION
# =========================================================


@login_required
@role_required("job_seeker")
def upload_resume(request):
    profile_obj, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.profile = profile_obj
            resume.save()
            messages.success(request, "Resume uploaded successfully!")
            return redirect("accounts:resume_list")
    else:
        form = ResumeForm()
    return render(request, "accounts/upload_resume.html", {"form": form})


@login_required
@role_required("job_seeker")
def resume_list(request):
    profile_obj, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    resumes = Resume.objects.filter(profile=profile_obj).order_by("-uploaded_at")
    return render(request, "accounts/resume_list.html", {"resumes": resumes})


@login_required
@role_required("job_seeker")
def set_default_resume(request, resume_id):
    profile_obj = get_object_or_404(JobSeekerProfile, user=request.user)
    resume = get_object_or_404(Resume, id=resume_id, profile=profile_obj)
    Resume.objects.filter(profile=profile_obj).update(is_default=False)
    resume.is_default = True
    resume.save()
    messages.success(request, "Default resume updated successfully.")
    return redirect("accounts:resume_list")


@login_required
@role_required("job_seeker")
def delete_resume(request, resume_id):
    profile_obj = get_object_or_404(JobSeekerProfile, user=request.user)
    resume = get_object_or_404(Resume, id=resume_id, profile=profile_obj)
    resume.file.delete(save=False)
    resume.delete()
    messages.success(request, "Resume deleted successfully.")
    return redirect("accounts:resume_list")


@login_required
def download_resume(request, resume_id):
    user_role = getattr(request.user, "role", None)
    if user_role == "employer" and not request.user.is_superuser:
        active_sub = (
            Subscription.objects.filter(user=request.user, status="active")
            .select_related("plan")
            .first()
        )
        if not active_sub:
            messages.error(
                request, "An active subscription is required to download resumes."
            )
            return redirect("billing:subscription_plans")

        usage, _ = SubscriptionUsage.objects.get_or_create(subscription=active_sub)
        if (
            active_sub.plan.resume_download_limit > 0
            and usage.resumes_downloaded >= active_sub.plan.resume_download_limit
        ):
            messages.error(request, "You have reached your resume download limit.")
            return redirect("billing:subscription_plans")

        usage.resumes_downloaded += 1
        usage.save(update_fields=["resumes_downloaded"])

    resume = get_object_or_404(Resume, id=resume_id)
    return redirect(resume.file.url)


# =========================================================
# COMPANY & JOB MANAGEMENT
# =========================================================


@login_required
@role_required("employer")
def create_company(request):
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.employer = request.user
            company.save()
            messages.success(request, "Company created successfully!")
            return redirect("accounts:employer_company")
    else:
        form = CompanyForm()
    return render(request, "accounts/create_company.html", {"form": form})


@login_required
@role_required("employer")
def employer_company(request):
    companies = Company.objects.filter(employer=request.user)
    return render(request, "accounts/employer_company.html", {"companies": companies})


@login_required
@role_required("employer")
def create_job(request):
    active_sub = None
    if not request.user.is_superuser:
        active_sub = (
            Subscription.objects.filter(user=request.user, status="active")
            .select_related("plan")
            .first()
        )
        if not active_sub:
            messages.error(
                request, "An active subscription plan is required to post jobs."
            )
            return redirect("billing:subscription_plans")

        usage, _ = SubscriptionUsage.objects.get_or_create(subscription=active_sub)
        if (
            active_sub.plan.job_post_limit > 0
            and usage.jobs_posted >= active_sub.plan.job_post_limit
        ):
            messages.error(request, "You have reached your job posting limit.")
            return redirect("billing:subscription_plans")

    company_obj, created = Company.objects.get_or_create(
        employer=request.user, defaults={"name": request.user.username}
    )

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company_obj
            if active_sub and active_sub.plan.can_feature_jobs:
                job.is_featured = True
            job.is_approved = True
            job.save()
            form.save_m2m()

            if active_sub:
                usage.jobs_posted += 1
                usage.save(update_fields=["jobs_posted"])

            messages.success(request, "Job successfully published and is now live!")
            return redirect("accounts:employer_jobs")
    else:
        form = JobForm()

    return render(request, "accounts/create_job.html", {"form": form})


@login_required
@role_required("employer")
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.company.employer != request.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit this job.")
        return redirect("accounts:employer_jobs")

    if request.method == "POST":
        form = JobForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Job successfully updated!")
            return redirect("accounts:employer_jobs")
    else:
        form = JobForm(instance=job, user=request.user)

    return render(request, "accounts/edit_job.html", {"form": form, "job": job})


@login_required
@role_required("employer")
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.company.employer != request.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this job.")
        return redirect("accounts:employer_jobs")

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job successfully deleted!")
        return redirect("accounts:employer_jobs")

    return render(request, "accounts/job_confirm_delete.html", {"job": job})


@login_required
@role_required("employer")
def employer_jobs(request):
    jobs = (
        Job.objects.filter(company__employer=request.user)
        .select_related("company", "category", "industry")
        .order_by("-created_at")
    )
    return render(request, "accounts/employer_jobs.html", {"jobs": jobs})


@login_required
@role_required("employer")
def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, company__employer=request.user)
    job.is_active = not job.is_active
    job.save()
    messages.success(request, "Job status updated successfully.")
    return redirect("accounts:employer_jobs")


# =========================================================
# ADMIN JOBS
# =========================================================


@login_required
@role_required("admin")
def admin_jobs(request):
    jobs = Job.objects.all().order_by("-created_at")
    return render(request, "accounts/admin_jobs.html", {"jobs": jobs})


@login_required
@role_required("admin")
def approve_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.is_approved = True
    job.save()
    messages.success(request, f"Job '{job.title}' approved successfully.")
    return redirect("accounts:admin_jobs")


# =========================================================
# JOB LIST, SEARCH & APPLICATIONS
# =========================================================


@login_required
def job_list(request):
    user = request.user
    user_role = str(getattr(user, "role", "")).lower()
    is_employer = "employer" in user_role

    if is_employer:
        user_company = Company.objects.filter(employer=user).first()
        if user_company:
            jobs = Job.objects.filter(company=user_company)
        else:
            jobs = Job.objects.filter(company__employer=user)
    else:
        jobs = Job.objects.filter(is_approved=True, is_active=True)
        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(company__name__icontains=keyword)
            )

        location = request.GET.get("location", "").strip()
        if location:
            jobs = jobs.filter(location__icontains=location)

    jobs = jobs.distinct().order_by("-created_at")

    return render(
        request,
        "accounts/job_list.html",
        {
            "jobs": jobs,
            "is_employer": is_employer,
            "categories": JobCategory.objects.filter(is_active=True),
            "industries": Industry.objects.filter(is_active=True),
        },
    )


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job_schema = generate_job_posting_schema(job, request)
    return render(
        request, "accounts/job_detail.html", {"job": job, "job_schema": job_schema}
    )


def toggle_save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    saved_post = SavedPost.objects.filter(user=request.user, post=post)

    if saved_post.exists():
        saved_post.delete()
    else:
        SavedPost.objects.create(user=request.user, post=post)

    return redirect("post_detail", post_id=post.id)


@login_required
@role_required("job_seeker")
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_approved=True, is_active=True)
    SavedJob.objects.get_or_create(user=request.user, job=job)
    messages.success(request, "Job saved successfully!")
    return redirect("accounts:job_detail", job_id=job.id)


@login_required
@role_required("job_seeker")
def unsave_job(request, job_id):
    SavedJob.objects.filter(user=request.user, job_id=job_id).delete()
    messages.info(request, "Job removed from saved jobs.")
    return redirect("accounts:job_detail", job_id=job_id)


@login_required
@role_required("job_seeker")
def saved_jobs(request):
    saved_jobs = (
        SavedJob.objects.filter(user=request.user)
        .select_related("job", "job__company")
        .order_by("-saved_at")
    )
    return render(request, "accounts/saved_jobs.html", {"saved_jobs": saved_jobs})


@login_required
def saved_posts_list(request):
    saved_posts = SavedPost.objects.filter(user=request.user).order_by("-created_at")

    context = {"saved_posts": saved_posts}
    return render(request, "accounts/saved_posts.html", context)


import google.generativeai as genai
from django.conf import settings

# Gemini configure karein
genai.configure(api_key=settings.GEMINI_API_KEY)


@login_required
@role_required("job_seeker")
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_approved=True, is_active=True)

    already_applied = Application.objects.filter(
        job=job, applicant=request.user
    ).exists()

    if already_applied:
        messages.warning(request, "You have already applied for this job.")
        return redirect("accounts:my_applications")

    resumes = Resume.objects.filter(profile__user=request.user)

    if request.method == "POST":
        resume_id = request.POST.get("resume")
        cover_letter = request.POST.get("cover_letter", "")
        resume = None

        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)

        ats_score = 75.0

        THRESHOLD = 60.0
        if ats_score >= THRESHOLD:
            app_status = "selected"
            email_subject = f"Congratulations! Application Accepted for {job.title}"
            email_message = (
                f"Hi {request.user.username},\n\n"
                f"Great news! Your application for {job.title} at {job.company.name} has been accepted based on your strong ATS score of {ats_score}%.\n\n"
                "Best regards,\nSmartJobs Team"
            )
        else:
            app_status = "rejected"
            email_subject = f"Update on your application for {job.title}"
            email_message = (
                f"Hi {request.user.username},\n\n"
                f"Thank you for applying for {job.title}. Unfortunately, your ATS score ({ats_score}%) did not meet our current requirements for this role.\n\n"
                "Best regards,\nSmartJobs Team"
            )

        Application.objects.create(
            job=job,
            applicant=request.user,
            resume=resume,
            cover_letter=cover_letter,
            status=app_status,
        )

        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email error: {e}")

        if app_status == "selected":
            messages.success(
                request,
                f"Application Accepted! ATS Score: {ats_score}%. Email notification sent.",
            )
        else:
            messages.warning(
                request,
                f"Application evaluated. ATS Score: {ats_score}%. Status: Rejected.",
            )

        return redirect("accounts:my_applications")

    return render(request, "accounts/apply_job.html", {"job": job, "resumes": resumes})


@login_required
@role_required("job_seeker")
def generate_ai_cover_letter(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Job, id=job_id)
        user = request.user

        profile = getattr(user, "job_seeker_profile", None)
        skills = (
            ", ".join([s.skill.name for s in profile.skills.all()])
            if profile
            else "General Skills"
        )

        prompt = f"""
        Act as a professional human job applicant writing an email/cover letter. Write a short, natural, and engaging cover letter for the following job.
        
        Job Title: {job.title}
        Company: {job.company.name}
        Job Description: {job.description[:400]}
        
        Applicant Name: {user.get_full_name() or user.username}
        Applicant Skills: {skills}

        Instructions:
        - Write in a natural, conversational, yet professional human tone.
        - STRICTLY AVOID robotic AI cliché phrases like "I am thrilled to submit", "In today's fast-paced world", "As a passionate professional", or "Dear Hiring Manager".
        - Keep it concise (around 3 short paragraphs).
        - Focus directly on how the applicant's experience fits the company's needs.
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            cover_letter_text = response.text.strip()

            return JsonResponse({"success": True, "cover_letter": cover_letter_text})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid method"}, status=400)


@login_required
@role_required("job_seeker")
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).select_related(
        "job", "job__company", "resume"
    )
    return render(
        request, "accounts/my_applications.html", {"applications": applications}
    )


@login_required
@role_required("employer")
def job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, company__employer=request.user)
    applications = Application.objects.filter(job=job).select_related(
        "applicant", "resume"
    )
    return render(
        request,
        "accounts/job_applicants.html",
        {"job": job, "applications": applications},
    )


@login_required
@role_required("employer")
def update_application_status(request, application_id):
    application = get_object_or_404(
        Application, id=application_id, job__company__employer=request.user
    )
    if request.method == "POST":
        status = request.POST.get("status")
        valid_statuses = [
            "applied",
            "shortlisted",
            "interview",
            "selected",
            "rejected",
            "withdrawn",
        ]
        if status in valid_statuses:
            application.status = status
            application.save()
            messages.success(
                request, f"Application status updated to {status.capitalize()}."
            )

    return redirect("accounts:job_applicants", job_id=application.job.id)


# =========================================================
# SOCIAL POSTS & INTERACTIONS (WITH UPDATED NOTIFICATIONS)
# =========================================================


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect("accounts:dashboard")
    else:
        form = PostForm()
    return render(request, "accounts/create_post.html", {"form": form})


@login_required
def feed(request):
    return redirect("accounts:dashboard")


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    like = PostLike.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
        Notification.objects.filter(
            user=post.author,
            sender=request.user,
            message__icontains="liked your post",
        ).delete()
    else:
        PostLike.objects.create(user=request.user, post=post)
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                sender=request.user,
                title="Post Liked",
                message=f"{request.user.username} liked your post.",
                channel="IN_APP",
            )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"success": True, "post_id": post.id, "likes_count": post.likes.count()}
        )

    return redirect("accounts:dashboard")


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            PostComment.objects.create(user=request.user, post=post, content=content)

            if post.author != request.user:
                Notification.objects.create(
                    user=post.author,
                    sender=request.user,
                    title="New Comment",
                    message=f"{request.user.username} commented on your post.",
                )
    return redirect("accounts:dashboard")


@login_required
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(PostComment, id=comment_id, is_active=True)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            PostComment.objects.create(
                user=request.user,
                post=parent_comment.post,
                parent=parent_comment,
                content=content,
            )

            if parent_comment.user != request.user:
                Notification.objects.create(
                    user=parent_comment.user,
                    sender=request.user,
                    title="New Reply",
                    message=f"{request.user.username} replied to your comment.",
                )
    return redirect("accounts:dashboard")


@login_required
def toggle_repost(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    repost = Repost.objects.filter(user=request.user, post=post).first()

    if repost:
        repost.delete()
        Notification.objects.filter(
            user=post.author,
            sender=request.user,
            message__icontains="reposted your post",
        ).delete()
    else:
        Repost.objects.create(user=request.user, post=post)

        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                sender=request.user,
                title="New Repost",
                message=f"{request.user.username} reposted your post.",
            )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "post_id": post.id,
                "reposts_count": post.reposted_by.count(),
            }
        )

    return redirect("accounts:dashboard")


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        remove_image = request.POST.get("remove_image") == "true"
        new_image = request.FILES.get("image")

        if content:
            post.content = content
            if remove_image:
                post.image.delete(save=False)
                post.image = None
            elif new_image:
                post.image = new_image
            post.save()
            messages.success(request, "Post updated successfully!")
            return redirect("accounts:dashboard")

    return render(request, "accounts/edit_post.html", {"post": post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect("accounts:dashboard")

    post.delete()
    messages.success(request, "Post deleted successfully!")
    return redirect("accounts:dashboard")


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(PostComment, id=comment_id)
    if comment.user == request.user or comment.post.author == request.user:
        comment.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "comment_id": comment_id, "post_id": comment.post.id}
            )
    return redirect("accounts:dashboard")


# =========================================================
# PEOPLE & CONNECTIONS
# =========================================================


@login_required
def people(request):
    search_query = request.GET.get("q", "").strip()
    skill_filter = request.GET.get("skill", "").strip()
    location_filter = request.GET.get("location", "").strip()

    people_list = User.objects.exclude(id=request.user.id).filter(is_active=True)

    user_role = getattr(request.user, "role", "")
    if user_role and str(user_role).lower() == "employer":
        people_list = people_list.filter(role__iexact="job_seeker")

    if search_query:
        search_filter = (
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )
        if hasattr(User, "headline"):
            search_filter |= Q(headline__icontains=search_query)
        people_list = people_list.filter(search_filter)

    if location_filter and hasattr(User, "location"):
        people_list = people_list.filter(location__icontains=location_filter)

    people_list = people_list.distinct().order_by("username")
    people_list = people_list.annotate(
        is_following=Exists(
            Follow.objects.filter(follower=request.user, following=OuterRef("pk"))
        )
    )

    return render(
        request,
        "accounts/people.html",
        {
            "people": people_list,
            "search_query": search_query,
            "skill_filter": skill_filter,
            "location_filter": location_filter,
        },
    )


@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile_obj = getattr(profile_user, "job_seeker_profile", None)

    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    is_following = Follow.objects.filter(
        follower=request.user, following=profile_user
    ).exists()

    connection = Connection.objects.filter(
        sender=request.user, receiver=profile_user
    ).first()

    reverse_connection = Connection.objects.filter(
        sender=profile_user, receiver=request.user
    ).first()

    followers = [
        f.follower
        for f in Follow.objects.filter(following=profile_user).select_related(
            "follower"
        )
    ]
    following_users = [
        f.following
        for f in Follow.objects.filter(follower=profile_user).select_related(
            "following"
        )
    ]

    sent_conns = Connection.objects.filter(sender=profile_user, status="accepted")
    recv_conns = Connection.objects.filter(receiver=profile_user, status="accepted")
    connections = [
        c.receiver if c.sender == profile_user else c.sender
        for c in (list(sent_conns) + list(recv_conns))
    ]

    return render(
        request,
        "accounts/user_profile.html",
        {
            "profile_user": profile_user,
            "profile": profile_obj,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
            "connection": connection,
            "reverse_connection": reverse_connection,
            "followers": followers,
            "following_users": following_users,
            "connections": connections,
        },
    )


@login_required
def toggle_follow(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return redirect("accounts:profile")

    follow = Follow.objects.filter(follower=request.user, following=target_user).first()

    if follow:
        follow.delete()
        Notification.objects.filter(
            user=target_user,
            sender=request.user,
            message__icontains="started following you",
        ).delete()
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        Notification.objects.create(
            user=target_user,
            sender=request.user,
            title="New Follower",
            message=f"{request.user.username} started following you.",
        )

    return redirect(request.META.get("HTTP_REFERER", "accounts:people"))


@login_required
def send_connection(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if (
        receiver == request.user
        or Connection.objects.filter(sender=request.user, receiver=receiver).exists()
    ):
        return redirect("accounts:user_profile", user_id=user_id)

    if Connection.objects.filter(sender=receiver, receiver=request.user).exists():
        return redirect("accounts:user_profile", user_id=user_id)

    Connection.objects.create(sender=request.user, receiver=receiver, status="pending")

    Notification.objects.create(
        user=receiver,
        sender=request.user,
        title="Connection Request",
        message=f"{request.user.username} sent you a connection request.",
    )

    messages.success(request, "Connection request sent successfully!")
    return redirect("accounts:user_profile", user_id=user_id)


@login_required
def accept_connection(request, connection_id):
    connection = get_object_or_404(
        Connection, id=connection_id, receiver=request.user, status="pending"
    )
    connection.status = "accepted"
    connection.save()

    Notification.objects.create(
        user=connection.sender,
        sender=request.user,
        title="Connection Accepted",
        message=f"{request.user.username} accepted your connection request.",
    )

    messages.success(request, "Connection request accepted.")
    return redirect("notifications:notification_list")


@login_required
def reject_connection(request, connection_id):
    connection = get_object_or_404(
        Connection, id=connection_id, receiver=request.user, status="pending"
    )
    connection.delete()
    messages.info(request, "Connection request rejected.")
    return redirect("notifications:notification_list")


@login_required
def global_search(request):
    query = request.GET.get("q", "")
    search_type = request.GET.get("type", "job")

    if search_type == "people":
        return redirect(f"/people/?q={query}")
    else:
        return redirect(f"/jobs/list/?keyword={query}")
