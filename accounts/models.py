from django.db import models
from django.contrib.auth.models import AbstractUser

# =========================================================
# CUSTOM USER
# =========================================================


class User(AbstractUser):

    ROLE_CHOICES = [
        ("job_seeker", "Job Seeker"),
        ("employer", "Employer"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="job_seeker")

    phone = models.CharField(max_length=15, blank=True)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# =========================================================
# JOB SEEKER PROFILE
# =========================================================


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="job_seeker_profile"
    )
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    # 🟢 CHANGED: URLField -> ImageField
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# =========================================================
# SKILL
# =========================================================


class Skill(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# =========================================================
# JOB SEEKER SKILL
# =========================================================


class JobSeekerSkill(models.Model):

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="skills"
    )

    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="job_seekers"
    )

    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def __str__(self):
        return f"{self.profile.user.username} - {self.skill.name}"


# =========================================================
# EDUCATION
# =========================================================


class Education(models.Model):

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="education"
    )

    institution = models.CharField(max_length=200)

    degree = models.CharField(max_length=100)

    field_of_study = models.CharField(max_length=150, blank=True)

    start_year = models.PositiveIntegerField()

    end_year = models.PositiveIntegerField(null=True, blank=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.user.username} - {self.degree}"


# =========================================================
# EXPERIENCE
# =========================================================


class Experience(models.Model):

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="experiences"
    )

    company_name = models.CharField(max_length=200)

    job_title = models.CharField(max_length=150)

    location = models.CharField(max_length=150, blank=True)

    start_date = models.DateField()

    end_date = models.DateField(null=True, blank=True)

    is_current = models.BooleanField(default=False)

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.user.username} - {self.job_title}"


# =========================================================
# RESUME
# =========================================================


class Resume(models.Model):

    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="resumes"
    )

    title = models.CharField(max_length=150)

    file = models.FileField(upload_to="resumes/")

    is_default = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username} - {self.title}"


# =========================================================
# JOB CATEGORY
# =========================================================


class JobCategory(models.Model):

    name = models.CharField(max_length=100, unique=True)

    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================================================
# INDUSTRY
# =========================================================


class Industry(models.Model):

    name = models.CharField(max_length=100, unique=True)

    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================================================
# COMPANY
# =========================================================


class Company(models.Model):

    employer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="companies"
    )

    name = models.CharField(max_length=200)

    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)

    description = models.TextField(blank=True)

    website = models.URLField(blank=True)

    location = models.CharField(max_length=200)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================================
# JOB
# =========================================================


class Job(models.Model):

    EMPLOYMENT_TYPES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    WORK_MODES = [
        ("onsite", "Onsite"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )

    industry = models.ForeignKey(
        Industry, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs"
    )

    location = models.CharField(max_length=200)

    salary_min = models.PositiveIntegerField(null=True, blank=True)

    salary_max = models.PositiveIntegerField(null=True, blank=True)

    experience_min = models.PositiveIntegerField(default=0)

    experience_max = models.PositiveIntegerField(null=True, blank=True)

    employment_type = models.CharField(
        max_length=30, choices=EMPLOYMENT_TYPES, default="full_time"
    )

    work_mode = models.CharField(max_length=20, choices=WORK_MODES, default="onsite")

    skills = models.ManyToManyField(Skill, blank=True, related_name="jobs")

    is_featured = models.BooleanField(default=False)

    is_urgent = models.BooleanField(default=False)

    is_approved = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================================================
# SAVED JOB
# =========================================================


class SavedJob(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "job"], name="unique_saved_job")
        ]

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


# =========================================================
# APPLICATION
# =========================================================


class Application(models.Model):

    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("selected", "Selected"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")

    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )

    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    cover_letter = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")

    applied_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "applicant"], name="unique_job_application"
            )
        ]

        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


# =========================================================
# SOCIAL POST
# =========================================================


class Post(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    content = models.TextField()

    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.author.username} - {self.content[:50]}"


# =========================================================
# POST LIKE
# =========================================================


class PostLike(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_post_like")
        ]

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"


# =========================================================
# POST COMMENT
# =========================================================


class PostComment(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_comments"
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - Post {self.post.id}"


# =========================================================
# REPOST
# =========================================================


class Repost(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reposts")

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reposted_by")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_repost")
        ]

    def __str__(self):
        return f"{self.user.username} reposted Post {self.post.id}"

    # =========================================================
    # SAVED POST
    # =========================================================


class SavedPost(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_by")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_saved_post")
        ]

    def __str__(self):
        return f"{self.user.username} saved Post {self.post.id}"


# =========================================================
# FOLLOW
# =========================================================


class Follow(models.Model):

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            )
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


# =========================================================
# CONNECTION
# =========================================================


class Connection(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_connections"
    )

    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_connections"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"], name="unique_connection_request"
            )
        ]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"


# =========================================================
# NOTIFICATION
# =========================================================


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ("like", "Like"),
        ("comment", "Comment"),
        ("reply", "Reply"),
        ("repost", "Repost"),
        ("follow", "Follow"),
        ("connection", "Connection"),
        ("application", "Application"),
        ("job", "Job"),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
    )

    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)

    message = models.CharField(max_length=255)

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.message}"


from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)  # e.g. 10% or 20%
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        now = timezone.now()
        return (
            self.active
            and self.valid_from <= now <= self.valid_to
            and self.used_count < self.max_uses
        )

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% OFF"


class Certification(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=150)  # e.g. AWS Certified Developer
    issuing_organization = models.CharField(max_length=150)  # e.g. Amazon Web Services
    issue_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"
