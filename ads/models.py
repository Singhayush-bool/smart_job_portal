from django.conf import settings
from django.db import models


# =========================================================
# 1. AD CAMPAIGN MODEL
# =========================================================
class AdCampaign(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    )

    advertiser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    title = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_date = models.DateField()
    end_date = models.DateField()

    # Targeting Parameters
    target_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="e.g. Mumbai, Bangalore",
    )
    target_industry = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g. IT, Healthcare"
    )
    target_skills = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Comma-separated: Python, React",
    )
    target_exp_min = models.PositiveIntegerField(
        default=0, help_text="Min Experience in years"
    )
    target_exp_max = models.PositiveIntegerField(
        default=30, help_text="Max Experience in years"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.advertiser.username}"


# =========================================================
# 2. ADVERTISEMENT & PLACEMENT MODEL
# =========================================================
class Advertisement(models.Model):
    AD_TYPE_CHOICES = (
        ("banner", "Banner Ad"),
        ("homepage", "Homepage Ad"),
        ("search", "Search Page Ad"),
        ("category", "Category Ad"),
        ("sidebar", "Sidebar Ad"),
        ("mobile", "Mobile Ad"),
        ("sponsored_job", "Sponsored Job"),
        ("featured_company", "Featured Company"),
        ("sponsored_recruiter", "Sponsored Recruiter"),
    )

    campaign = models.ForeignKey(
        AdCampaign, on_delete=models.CASCADE, related_name="ads"
    )
    ad_type = models.CharField(max_length=30, choices=AD_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    banner_image = models.ImageField(upload_to="ads/banners/", blank=True, null=True)
    destination_url = models.URLField(help_text="Landing URL when user clicks ad")
    is_active = models.BooleanField(default=True)

    # Optional internal object links
    sponsored_job_id = models.IntegerField(
        blank=True, null=True, help_text="Job ID if Sponsored Job"
    )
    featured_company_id = models.IntegerField(
        blank=True, null=True, help_text="Company ID if Featured Company"
    )

    # Performance Analytics
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    cpc = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=5.00,
        help_text="Cost Per Click (₹)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_ad_type_display()} - {self.title}"

    @property
    def ctr(self):
        """Calculates Click-Through Rate (CTR %)"""
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)

    @property
    def total_revenue(self):
        """Calculates Total Revenue Earned (Clicks * CPC)"""
        return round(float(self.clicks) * float(self.cpc), 2)
