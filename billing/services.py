from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import (
    Subscription,
    SubscriptionUsage,
    Coupon,
    Transaction as BillingTransaction,
    Invoice,
    Wallet,
    WalletTransaction,
)

# =========================================================
# ACTIVE SUBSCRIPTION
# =========================================================


def get_active_subscription(user):
    """
    Return user's active subscription.
    Expired subscriptions are automatically marked expired.
    """
    subscription = (
        Subscription.objects.filter(
            user=user,
            status="active",
        )
        .select_related("plan")
        .first()
    )

    if not subscription:
        return None

    if subscription.end_date and subscription.end_date <= timezone.now():
        subscription.status = "expired"
        subscription.save(update_fields=["status", "updated_at"])
        return None

    return subscription


# =========================================================
# SUBSCRIPTION USAGE & ACCESS CHECKS
# =========================================================


def get_subscription_usage(subscription):
    """Get or create usage record for a subscription."""
    usage, created = SubscriptionUsage.objects.get_or_create(subscription=subscription)
    return usage


def can_post_job(user):
    subscription = get_active_subscription(user)
    if not subscription:
        return False

    plan = subscription.plan
    usage = get_subscription_usage(subscription)

    if plan.job_post_limit == 0:  # 0 means unlimited
        return True

    return usage.jobs_posted < plan.job_post_limit


def can_download_resume(user):
    subscription = get_active_subscription(user)
    if not subscription:
        return False

    plan = subscription.plan
    usage = get_subscription_usage(subscription)

    if plan.resume_download_limit == 0:  # 0 means unlimited
        return True

    return usage.resumes_downloaded < plan.resume_download_limit


def can_feature_job(user):
    subscription = get_active_subscription(user)
    return subscription.plan.featured_jobs if subscription else False


def has_company_branding(user):
    subscription = get_active_subscription(user)
    return subscription.plan.company_branding if subscription else False


def has_analytics_access(user):
    subscription = get_active_subscription(user)
    return subscription.plan.analytics if subscription else False


def has_priority_support(user):
    subscription = get_active_subscription(user)
    return subscription.plan.priority_support if subscription else False


# =========================================================
# INCREMENT USAGE COUNTERS
# =========================================================


def increment_job_usage(user):
    subscription = get_active_subscription(user)
    if not subscription:
        return False

    usage = get_subscription_usage(subscription)
    usage.jobs_posted += 1
    usage.save(update_fields=["jobs_posted", "updated_at"])
    return True


def increment_resume_download_usage(user):
    subscription = get_active_subscription(user)
    if not subscription:
        return False

    usage = get_subscription_usage(subscription)
    usage.resumes_downloaded += 1
    usage.save(update_fields=["resumes_downloaded", "updated_at"])
    return True


def increment_featured_job_usage(user):
    subscription = get_active_subscription(user)
    if not subscription:
        return False

    usage = get_subscription_usage(subscription)
    usage.featured_jobs_used += 1
    usage.save(update_fields=["featured_jobs_used", "updated_at"])
    return True


# =========================================================
# GST & COUPON CALCULATIONS
# =========================================================


def apply_coupon_discount(coupon_code, base_amount):
    """Validates coupon and returns discount amount, coupon object, or error."""
    if not coupon_code:
        return Decimal("0.00"), None, None

    try:
        coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
    except Coupon.DoesNotExist:
        return Decimal("0.00"), None, "Invalid coupon code."

    now = timezone.now()
    if coupon.valid_from > now or coupon.valid_to < now:
        return Decimal("0.00"), None, "Coupon has expired."

    if coupon.used_count >= coupon.usage_limit:
        return Decimal("0.00"), None, "Coupon usage limit reached."

    if base_amount < coupon.min_purchase_amount:
        return (
            Decimal("0.00"),
            None,
            f"Min purchase of ₹{coupon.min_purchase_amount} required.",
        )

    if coupon.discount_type == "percentage":
        discount = (base_amount * coupon.discount_value) / Decimal("100")
        if coupon.max_discount_amount and discount > coupon.max_discount_amount:
            discount = coupon.max_discount_amount
    else:
        discount = coupon.discount_value

    discount = min(discount, base_amount)
    return discount, coupon, None


def calculate_gst(amount, gst_rate=18, is_interstate=False):
    """Calculates 18% GST tax breakdown."""
    gst_amount = (amount * Decimal(gst_rate)) / Decimal("100")
    if is_interstate:
        cgst = Decimal("0.00")
        sgst = Decimal("0.00")
        igst = gst_amount
    else:
        cgst = gst_amount / Decimal("2")
        sgst = gst_amount / Decimal("2")
        igst = Decimal("0.00")

    return {
        "gst_amount": gst_amount,
        "cgst": cgst,
        "sgst": sgst,
        "igst": igst,
        "total_amount": amount + gst_amount,
    }


# =========================================================
# WALLET OPERATIONS
# =========================================================


def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


@transaction.atomic
def process_wallet_payment(user, amount, description="Subscription Payment"):
    wallet = get_or_create_wallet(user)
    if wallet.balance < amount:
        return False, "Insufficient wallet balance."

    wallet.balance -= amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type="debit",
        description=description,
    )
    return True, "Payment successful."
