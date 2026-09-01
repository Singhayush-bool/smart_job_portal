from django.contrib import admin
from .models import SubscriptionPlan, Subscription, SubscriptionUsage, PaymentHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "job_post_limit",
        "resume_download_limit",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "start_date", "end_date")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__email")


@admin.register(SubscriptionUsage)
class SubscriptionUsageAdmin(admin.ModelAdmin):
    list_display = ("subscription", "jobs_posted", "resumes_downloaded")


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "razorpay_order_id", "razorpay_payment_id")


from django.contrib import admin
from .models import (
    Coupon,
    PaymentHistory,
    Subscription,
    SubscriptionPlan,
    SubscriptionUsage,
)


# Agar Coupon model billing/models.py me hai, toh isse add karein:
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "valid_from", "valid_to", "active")
    list_filter = ("active",)
    search_fields = ("code",)
