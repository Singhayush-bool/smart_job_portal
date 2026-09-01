from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def create_google_meet(event_title, start_time_iso, end_time_iso, user_creds_dict):
    try:
        creds = Credentials.from_authorized_user_info(user_creds_dict)
        service = build("calendar", "v3", credentials=creds)

        event_body = {
            "summary": event_title,
            "start": {"dateTime": start_time_iso, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time_iso, "timeZone": "Asia/Kolkata"},
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{event_title.replace(' ', '-')}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }

        created_event = (
            service.events()
            .insert(calendarId="primary", body=event_body, conferenceDataVersion=1)
            .execute()
        )

        return {"status": "success", "meet_link": created_event.get("hangoutLink")}
    except Exception as e:
        return {"status": "error", "message": str(e)}
