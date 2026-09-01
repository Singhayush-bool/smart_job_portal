import json
import stripe
import razorpay
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from billing.models import Transaction, Subscription

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")


@csrf_exempt
def razorpay_webhook(request):
    """Razorpay Payment Status Webhook Verification"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        data = json.loads(request.body)
        client.utility.verify_webhook_signature(
            request.body.decode("utf-8"),
            request.headers.get("X-Razorpay-Signature"),
            settings.RAZORPAY_WEBHOOK_SECRET,
        )

        event = data.get("event")
        if event == "payment.captured":
            payment = data["payload"]["payment"]["entity"]
            tx_id = payment.get("notes", {}).get("transaction_id")
            if tx_id:
                tx = Transaction.objects.filter(id=tx_id).first()
                if tx:
                    tx.status = "SUCCESS"
                    tx.save()
                    # Activate subscription
                    if tx.subscription:
                        tx.subscription.status = "active"
                        tx.subscription.save()

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request):
    """Stripe Payment Intent Webhook Handler"""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        tx_id = intent.get("metadata", {}).get("transaction_id")
        if tx_id:
            tx = Transaction.objects.filter(id=tx_id).first()
            if tx:
                tx.status = "SUCCESS"
                tx.save()
                if tx.subscription:
                    tx.subscription.status = "active"
                    tx.subscription.save()

    return HttpResponse(status=200)
