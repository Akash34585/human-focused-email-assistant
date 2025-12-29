from pathlib import Path

FILES = [
    "data/raw_emails.json",
    "data/ai_outputs.json",
    "data/reply_drafts.json"
]

for file in FILES:
    path = Path(file)
    if path.exists():
        path.unlink()
