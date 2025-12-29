import base64
from gmail_service import get_gmail_service
from storage import save_raw_emails
from email_cleaner import clean_email
from email_filters import is_human_email
from datetime import datetime, timezone
import pytz


def get_email_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode(
                        "utf-8", errors="ignore"
                    )
    else:
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="ignore"
            )
    return ""


def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()


def fetch_unread_emails(max_results=5):
    service = get_gmail_service()

    query = (
        "is:unread "
        "in:inbox "
        "-category:promotions "
        "-category:social"
    )

    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    messages = response.get("messages", [])
    human_emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        utc_dt = datetime.fromtimestamp(
            int(msg_data["internalDate"]) / 1000,
            tz=timezone.utc
        )

        ist_tz = pytz.timezone("Asia/Kolkata")
        ist_dt = utc_dt.astimezone(ist_tz)

        headers = msg_data["payload"]["headers"]
        sender = ""
        subject = ""

        for h in headers:
            if h["name"].lower() == "from":
                sender = h["value"]
            elif h["name"].lower() == "subject":
                subject = h["value"]

        raw_body = get_email_body(msg_data["payload"])
        body = clean_email(raw_body)

        # 🔒 Mark EVERY fetched email as read
        mark_as_read(service, msg["id"])
        
        # ✅ Save ONLY human emails
        if is_human_email(sender, body):
            human_emails.append({
                "id": msg["id"],
                "from": sender,
                "subject": subject,
                "body": body,
                "received_at_utc": utc_dt.isoformat(),
                "received_at_ist": ist_dt.isoformat()
            })

    return human_emails


if __name__ == "__main__":
    emails = fetch_unread_emails()

    print(f"[DEBUG] Human emails found: {len(emails)}")

    if emails:
        save_raw_emails(emails)
