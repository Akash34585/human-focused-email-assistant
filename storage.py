import json
from datetime import datetime
from pathlib import Path
import pytz

ist = pytz.timezone("Asia/Kolkata")
RAW_EMAIL_FILE = Path("data/raw_emails.json")


def save_raw_emails(emails: list):
    RAW_EMAIL_FILE.parent.mkdir(exist_ok=True)
    print("[DEBUG] Saving raw_emails.json")

    payload = {
        "saved_at": datetime.now(ist).isoformat(),
        "count": len(emails),
        "emails": emails
    }

    with open(RAW_EMAIL_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
