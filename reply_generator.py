import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-oss-20b:free"

AI_OUTPUT_FILE = Path("data/ai_outputs.json")
REPLY_OUTPUT_FILE = Path("data/reply_drafts.json")


def call_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional executive assistant. "
                    "Write safe, neutral, and polite email replies. "
                    "Do NOT include subject lines. "
                    "Do NOT include signatures or placeholders. "
                    "Do NOT promise timelines, availability, or deadlines. "
                    "Never invent facts."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def build_reply_prompt(email: dict) -> str:
    analysis = email["analysis"]

    return f"""
Write a professional email reply.

Context:
Sender: {email['from']}
Subject: {email['subject']}

Summary:
- {'; '.join(analysis['summary'])}

Action Required: {analysis['action_required']}
Urgency: {analysis['urgency']}

Instructions:
- Be polite and human
- Acknowledge the message
- Keep it short (3–5 sentences)
- No subject line
- No signature
"""


def generate_replies():
    with open(AI_OUTPUT_FILE, "r", encoding="utf-8") as f:
        emails = json.load(f)

    replies = []

    for email in emails:
        reply_text = call_openrouter(
            build_reply_prompt(email)
        )

        replies.append({
            "id": email["id"],
            "from": email["from"],
            "subject": email["subject"],
            "reply_draft": reply_text
        })

    REPLY_OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(REPLY_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(replies, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generate_replies()
