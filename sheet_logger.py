import json
from datetime import datetime, timezone
import pytz
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
ist = pytz.timezone("Asia/Kolkata")
# ---- CONFIG ----
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_NAME = "Email Automation Log"

AI_OUTPUT_FILE = Path("data/ai_outputs.json")
REPLY_OUTPUT_FILE = Path("data/reply_drafts.json")

# ---- AUTH ----
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

def set_column_widths(sheet):
    sheet_id = sheet._properties["sheetId"]

    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 3,
                        "endIndex": 5
                    },
                    "properties": {
                        "pixelSize": 350
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }

    sheet.spreadsheet.batch_update(body)


def enable_wrap_text(sheet):
    sheet_id = sheet._properties["sheetId"]

    body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,   # skip header row
                        "startColumnIndex":0,
                        "endColumnIndex": 5     # Suggested Reply column (E)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields": "userEnteredFormat.wrapStrategy"
                }
            }
        ]
    }

    sheet.spreadsheet.batch_update(body)


def auto_resize_columns(sheet):
    sheet_id = sheet._properties["sheetId"]

    body = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,   # Column A
                        "endIndex": 6      # Up to column F (exclusive)
                    }
                }
            }
        ]
    }

    sheet.spreadsheet.batch_update(body)

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def log_to_sheet():
    ai_outputs = load_json(AI_OUTPUT_FILE)
    replies = load_json(REPLY_OUTPUT_FILE)

    reply_map = {
        r["id"]: r["reply_draft"]
        for r in replies
    }

    rows = []

    for email in ai_outputs:
        analysis = email["analysis"]

        received_time = datetime.fromisoformat(
            email["received_at_ist"]
        ).strftime("%Y-%m-%d %H:%M:%S")

        rows.append([
            received_time,
            email["from"],
            email["subject"],
            " | ".join(analysis["summary"]),
            reply_map.get(email["id"], ""),
            analysis["urgency"]
        ])

    if sheet.col_count < 6:
        set_column_widths(sheet)
        enable_wrap_text(sheet)

    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
        enable_wrap_text(sheet)



if __name__ == "__main__":
    log_to_sheet()
