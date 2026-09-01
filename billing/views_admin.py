from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from billing.models import Transaction, Subscription, Invoice


@staff_member_required
def revenue_dashboard(request):
    total_revenue = (
        Transaction.objects.filter(status="SUCCESS").aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0.0
    )
    active_subscriptions = Subscription.objects.filter(status="active").count()
    total_invoices = Invoice.objects.count()
    recent_transactions = Transaction.objects.order_by("-created_at")[:10]

    context = {
        "total_revenue": round(total_revenue, 2),
        "active_subscriptions": active_subscriptions,
        "total_invoices": total_invoices,
        "recent_transactions": recent_transactions,
    }
    return render(request, "billing/admin_revenue.html", context)
