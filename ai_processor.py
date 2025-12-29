import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import re
import json


load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-oss-20b:free"

RAW_EMAILS_FILE = Path("data/raw_emails.json")
AI_OUTPUT_FILE = Path("data/ai_outputs.json")


def load_raw_emails():
    with open(RAW_EMAILS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["emails"]


def call_openrouter(prompt: str) -> dict:
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
                "content": "You are a professional executive assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def build_prompt(email):
    return f"""
Analyze the email below and return a JSON object with the following fields:

- summary: 3 concise bullet points
- action_required: yes or no
- urgency: low, medium, or high

Rules:
- Be factual
- Do not invent deadlines
- If no action is needed, say "no"

Email:
From: {email['from']}
Subject: {email['subject']}
Body:
{email['body']}
"""


def process_emails():
    emails = load_raw_emails()
    results = []

    for email in emails:
        prompt = build_prompt(email)
        ai_response = call_openrouter(prompt)

        content = ai_response["choices"][0]["message"]["content"]
        parsed = extract_json_from_llm(content)

        results.append({
            "id": email["id"],
            "from": email["from"],
            "subject": email["subject"],
            "analysis": parsed,
            "received_at_utc": email["received_at_utc"],
            "received_at_ist": email["received_at_ist"]
        })


    AI_OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(AI_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def extract_json_from_llm(text: str) -> dict:
    """
    Safely extract JSON from LLM output
    Handles ```json ... ``` and raw JSON
    """
    if not text:
        raise ValueError("Empty LLM response")

    # Remove markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by LLM: {cleaned}") from e
    
if __name__ == "__main__":
    process_emails()
