# cms/models.py
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class SEOBaseModel(models.Model):
    """Abstract class to give SEO capabilities to all CMS models"""

    meta_title = models.CharField(max_length=70, blank=True, null=True)
    meta_description = models.TextField(max_length=160, blank=True, null=True)
    keywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Comma-separated keywords",
    )
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    canonical_url = models.URLField(blank=True, null=True)

    # Social Sharing (Open Graph / Twitter)
    og_title = models.CharField(max_length=100, blank=True, null=True)
    og_description = models.CharField(max_length=200, blank=True, null=True)
    og_image = models.ImageField(upload_to="seo/og_images/", blank=True)

    # Indexing Controls
    is_indexable = models.BooleanField(default=True)

    class Meta:
        abstract = True


class BlogPost(SEOBaseModel):
    CATEGORY_CHOICES = [
        ("career_tips", "Career Tips"),
        ("news", "News & Updates"),
        ("interview_prep", "Interview Preparation"),
        ("industry_trends", "Industry Trends"),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, default="SmartJobs Team")
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="career_tips"
    )
    featured_image = models.ImageField(upload_to="blog/images/", blank=True, null=True)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# --- Likes Model (Typo Fixed: auto_now_add) ---
class BlogLike(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blog", "user")


# --- Comments Model ---
class BlogComment(models.Model):
    blog = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.blog.title}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ("job_seeker", "Job Seeker"),
        ("employer", "Employer"),
        ("billing", "Billing & Payments"),
        ("general", "General"),
    ]

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="general"
    )
    order = models.PositiveIntegerField(default=0, help_text="Ordering position")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role_or_company = models.CharField(
        max_length=150, help_text="e.g. Software Engineer at TCS"
    )
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5, help_text="Rating out of 5")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.role_or_company}"


class StaticPage(SEOBaseModel):
    """About Us, Privacy Policy, Terms & Conditions, etc."""

    title = models.CharField(max_length=150)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
