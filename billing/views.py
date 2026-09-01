import razorpay
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Invoice,
    PaymentHistory,
    Subscription,
    SubscriptionPlan,
    SubscriptionUsage,
)

# Razorpay Client Setup
RAZORPAY_KEY_ID = getattr(settings, "RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = getattr(settings, "RAZORPAY_KEY_SECRET", "")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# =========================================================
# 1. SUBSCRIPTION PLANS VIEW
# =========================================================
@login_required
def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by("price")

    current_subscription = Subscription.objects.filter(
        user=request.user, status="active"
    ).first()

    usage = None
    if current_subscription:
        usage, _ = SubscriptionUsage.objects.get_or_create(
            subscription=current_subscription
        )

    return render(
        request,
        "billing/subscription_plans.html",
        {
            "plans": plans,
            "current_subscription": current_subscription,
            "usage": usage,
            "razorpay_key_id": RAZORPAY_KEY_ID,
        },
    )


# =========================================================
# 2. CREATE CHECKOUT SESSION (RAZORPAY ORDER)
# =========================================================
from .models import Coupon  # Imports mein add karein


@login_required
def create_checkout_session(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Free Plan direct activation
    if plan.price == 0:
        sub, _ = Subscription.objects.get_or_create(user=request.user)
        sub.plan = plan
        sub.status = "active"
        sub.start_date = timezone.now()
        sub.end_date = timezone.now() + timedelta(days=365 * 10)
        sub.save()

        SubscriptionUsage.objects.update_or_create(
            subscription=sub, defaults={"jobs_posted": 0, "resumes_downloaded": 0}
        )
        messages.success(request, f"Aapka {plan.name} plan activate ho gaya hai!")
        return redirect("billing:subscription_plans")

    # Coupon Processing
    discount_amount = 0
    final_price = float(plan.price)
    coupon_obj = None

    coupon_code = request.POST.get("coupon_code", "").strip()
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            if coupon.is_valid():
                discount_amount = (final_price * coupon.discount_percent) / 100
                final_price = max(0.0, final_price - discount_amount)
                coupon_obj = coupon
                messages.success(
                    request, f"Coupon '{coupon.code}' successfully apply ho gaya!"
                )
            else:
                messages.error(
                    request, "Yeh coupon code expire ya invalid ho chuka hai."
                )
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid Coupon Code.")

    # Razorpay Order Creation
    amount_in_paisa = int(final_price * 100)

    # In case discount makes price 0
    if amount_in_paisa == 0:
        sub, _ = Subscription.objects.get_or_create(user=request.user)
        sub.plan = plan
        sub.status = "active"
        sub.start_date = timezone.now()
        sub.end_date = timezone.now() + timedelta(days=30)
        sub.save()

        if coupon_obj:
            coupon_obj.used_count += 1
            coupon_obj.save()

        messages.success(request, "100% discount ke sath aapka plan activate ho gaya!")
        return redirect("billing:subscription_plans")

    razorpay_order = client.order.create(
        {"amount": amount_in_paisa, "currency": "INR", "payment_capture": "1"}
    )

    # Record Pending Payment
    PaymentHistory.objects.create(
        user=request.user,
        plan=plan,
        amount=final_price,
        razorpay_order_id=razorpay_order["id"],
        status="pending",
    )

    if coupon_obj and request.method == "POST":
        coupon_obj.used_count += 1
        coupon_obj.save()

    return render(
        request,
        "billing/checkout.html",
        {
            "plan": plan,
            "order_id": razorpay_order["id"],
            "amount": final_price,
            "original_amount": plan.price,
            "discount_amount": discount_amount,
            "razorpay_key_id": RAZORPAY_KEY_ID,
        },
    )


# =========================================================
# 3. PAYMENT SUCCESS CALLBACK & GST INVOICE GENERATION
# =========================================================
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id", "")
        order_id = request.POST.get("razorpay_order_id", "")
        signature = request.POST.get("razorpay_signature", "")

        params_dict = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }

        try:
            # Verify Signature
            client.utility.verify_payment_signature(params_dict)

            payment = get_object_or_404(PaymentHistory, razorpay_order_id=order_id)
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = "success"
            payment.save()

            # Activate Subscription
            user = payment.user
            plan = payment.plan

            sub, _ = Subscription.objects.get_or_create(user=user)
            sub.plan = plan
            sub.status = "active"
            sub.start_date = timezone.now()
            sub.end_date = timezone.now() + timedelta(days=30)  # 30 days validity
            sub.save()

            # Reset Usage Counters
            SubscriptionUsage.objects.update_or_create(
                subscription=sub, defaults={"jobs_posted": 0, "resumes_downloaded": 0}
            )

            # Auto-Generate GST (18%) Invoice
            total_val = float(plan.price)
            base_val = round(total_val / 1.18, 2)
            gst_val = round(total_val - base_val, 2)

            Invoice.objects.get_or_create(
                payment=payment,
                defaults={
                    "user": user,
                    "base_amount": base_val,
                    "gst_amount": gst_val,
                    "total_amount": total_val,
                },
            )

            messages.success(
                request, "Payment successful! Aapka plan activate ho gaya hai."
            )
            return redirect("billing:subscription_plans")

        except razorpay.errors.SignatureVerificationError:
            payment = PaymentHistory.objects.filter(razorpay_order_id=order_id).first()
            if payment:
                payment.status = "failed"
                payment.save()
            messages.error(
                request, "Payment verification fail ho gaya. Kripya dobara try karein."
            )
            return redirect("billing:subscription_plans")

    return HttpResponseBadRequest()


# =========================================================
# 4. MY SUBSCRIPTION VIEW
# =========================================================
@login_required
def my_subscription(request):
    subscription = Subscription.objects.filter(
        user=request.user, status="active"
    ).first()
    return render(
        request, "billing/my_subscription.html", {"subscription": subscription}
    )


# =========================================================
# 5. CANCEL SUBSCRIPTION
# =========================================================
@login_required
def cancel_subscription(request):
    if request.method == "POST":
        subscription = Subscription.objects.filter(
            user=request.user, status="active"
        ).first()
        if subscription:
            subscription.status = "cancelled"
            subscription.save()
            messages.success(request, "Your Subscribtion get cancelled.")
    return redirect("billing:my_subscription")


# =========================================================
# 6. INVOICE DETAIL VIEW
# =========================================================
@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    return render(request, "billing/invoice_detail.html", {"invoice": invoice})


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum


# =========================================================
# 7. PAYMENT HISTORY & INVOICE LIST (USER VIEW)
# =========================================================
@login_required
def payment_history_list(request):
    """Displays user's transaction history and generated GST invoices."""
    payments = (
        PaymentHistory.objects.filter(user=request.user)
        .select_related("plan")
        .order_by("-created_at")
    )

    invoices = (
        Invoice.objects.filter(user=request.user)
        .select_related("payment", "payment__plan")
        .order_by("-created_at")
    )

    return render(
        request,
        "billing/payment_history.html",
        {
            "payments": payments,
            "invoices": invoices,
        },
    )


# =========================================================
# 8. ADMIN REVENUE & SUBSCRIPTION ANALYTICS DASHBOARD
# =========================================================
@login_required
def admin_revenue_dashboard(request):
    """Financial & Subscription metrics dashboard for Admin."""
    if not (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        messages.error(request, "Access denied. Admin rights required.")
        return redirect("dashboard")

    now = timezone.now()

    # Total Revenue Earned (All Time)
    total_revenue = (
        PaymentHistory.objects.filter(status="success").aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0.0
    )

    # Monthly Recurring Revenue (Current Month Revenue)
    mrr = (
        PaymentHistory.objects.filter(
            status="success",
            created_at__month=now.month,
            created_at__year=now.year,
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0.0
    )

    # Subscriptions Breakdown
    active_subs = Subscription.objects.filter(status="active").count()
    cancelled_subs = Subscription.objects.filter(status="cancelled").count()

    # Total GST Collected
    total_gst = Invoice.objects.aggregate(Sum("gst_amount"))["gst_amount__sum"] or 0.0

    # Recent Transactions
    recent_payments = (
        PaymentHistory.objects.filter(status="success")
        .select_related("user", "plan")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "billing/admin_revenue_dashboard.html",
        {
            "total_revenue": round(total_revenue, 2),
            "mrr": round(mrr, 2),
            "active_subs": active_subs,
            "cancelled_subs": cancelled_subs,
            "total_gst": round(total_gst, 2),
            "recent_payments": recent_payments,
        },
    )


from .models import Coupon  # Ensure imported


# =========================================================
# 9. ADMIN SUBSCRIPTION & COUPON MANAGEMENT
# =========================================================
@login_required
def admin_manage_subscriptions(request):
    """Admin page to Create and Manage Subscription Plans & Coupons."""
    if not (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        messages.error(request, "Access denied. Admin rights required.")
        return redirect("dashboard")

    plans = SubscriptionPlan.objects.all().order_by("-created_at")
    coupons = Coupon.objects.all().order_by("-valid_to")

    if request.method == "POST" and "add_plan" in request.POST:
        SubscriptionPlan.objects.create(
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            job_post_limit=request.POST.get("job_post_limit") or 0,
            resume_download_limit=request.POST.get("resume_download_limit") or 0,
            can_feature_jobs="can_feature_jobs" in request.POST,
            company_branding="company_branding" in request.POST,
            priority_support="priority_support" in request.POST,
        )
        messages.success(request, "Naya Subscription Plan create ho gaya hai!")
        return redirect("billing:admin_manage_subscriptions")

    if request.method == "POST" and "add_coupon" in request.POST:
        Coupon.objects.create(
            code=request.POST.get("code").upper(),
            discount_percent=request.POST.get("discount_percent"),
            valid_from=request.POST.get("valid_from"),
            valid_to=request.POST.get("valid_to"),
            max_uses=request.POST.get("max_uses") or 100,
        )
        messages.success(request, "Naya Coupon Code add ho gaya hai!")
        return redirect("billing:admin_manage_subscriptions")

    return render(
        request,
        "billing/admin_manage_subscriptions.html",
        {"plans": plans, "coupons": coupons},
    )


@login_required
def delete_subscription_plan(request, plan_id):
    if not (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan.delete()
    messages.success(request, "Plan successfully remove kar diya gaya.")
    return redirect("billing:admin_manage_subscriptions")


@login_required
def toggle_plan_status(request, plan_id):
    if not (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    plan.is_active = not plan.is_active
    plan.save()
    messages.success(
        request,
        f"Plan status update ho gaya ({'Active' if plan.is_active else 'Disabled'}).",
    )
    return redirect("billing:admin_manage_subscriptions")
