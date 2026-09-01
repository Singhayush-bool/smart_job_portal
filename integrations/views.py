import time
from django.shortcuts import render
from django.http import JsonResponse


def test_panel_view(request):
    """Renders the third-party integrations testing dashboard."""
    return render(request, "integrations/test_panel.html")


def notify_whatsapp(request):
    """Handles WhatsApp notification requests via Twilio (Mock)."""
    if request.method == "POST":
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        if not phone:
            return JsonResponse({"error": "Phone number is required."}, status=400)

        # Mock Response
        return JsonResponse(
            {
                "status": "success",
                "message": f"WhatsApp message dispatched to {phone}",
                "payload": {"phone": phone, "message": message},
            },
            status=200,
        )
    return JsonResponse({"error": "Invalid method. Use POST."}, status=405)


def notify_push(request):
    """Handles Firebase FCM push notifications (Mock)."""
    if request.method == "POST":
        token = request.POST.get("token")
        title = request.POST.get("title", "SmartJobs Alert")
        body = request.POST.get("body")

        if not token:
            return JsonResponse({"error": "FCM token is required."}, status=400)

        # Mock Response
        return JsonResponse(
            {
                "status": "success",
                "message": "Push notification sent successfully",
                "payload": {"token": token, "title": title, "body": body},
            },
            status=200,
        )
    return JsonResponse({"error": "Invalid method. Use POST."}, status=405)


def upload_media(request):
    """Handles Cloudinary file uploads (Mock)."""
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"error": "No file uploaded."}, status=400)

        # Mock Response matching Cloudinary data structure
        file_name = file.name
        mock_public_id = f"smartjobs/demo_{int(time.time())}"

        return JsonResponse(
            {
                "status": "success",
                "message": f"File '{file_name}' processed successfully (Mock Cloudinary Upload).",
                "file_info": {
                    "name": file_name,
                    "size_bytes": file.size,
                    "public_id": mock_public_id,
                    "url": f"https://res.cloudinary.com/demo/image/upload/{mock_public_id}.jpg",
                    "format": (
                        file_name.split(".")[-1] if "." in file_name else "unknown"
                    ),
                },
            },
            status=200,
        )
    return JsonResponse({"error": "Invalid method. Use POST."}, status=405)
