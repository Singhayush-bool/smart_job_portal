import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase app instance safely
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    except Exception:
        pass


def send_push_notification(device_token, title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=device_token,
        )
        response = messaging.send(message)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}
