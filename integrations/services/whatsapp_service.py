from twilio.rest import Client
from django.conf import settings


def send_whatsapp_notification(to_number, text_message):
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_whatsapp = getattr(settings, "TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    if not account_sid or not auth_token:
        return {"status": "error", "message": "Twilio credentials missing in settings."}

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=from_whatsapp, body=text_message, to=f"whatsapp:{to_number}"
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}
