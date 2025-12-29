import re

HARD_BLOCK_KEYWORDS = [
    "no-reply",
    "noreply",
    "notification",
    "newsletter",
    "updates",
    "mailer",
    "unsubscribe"
]

HARD_BLOCK_DOMAINS = [
    # Social / platforms
    "facebookmail.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "instagram.com",

    # Gaming / accounts
    "epicgames.com",
    "acct.epicgames.com",
    "steamcommunity.com",
    "steampowered.com",

    # Auth / security
    "google.com",
    "accounts.google.com",
    "microsoft.com",

    # Freelance platforms
    "freelancer.com",
    "upwork.com",

    # E-commerce / payments
    "amazon",
    "flipkart",
    "paytm",
    "phonepe"
]


FREE_EMAIL_DOMAINS = [
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "icloud.com",
    "protonmail.com"
]


def is_hard_block(sender: str, body: str) -> bool:
    sender_l = sender.lower()
    body_l = body.lower()

    for k in HARD_BLOCK_KEYWORDS:
        if k in sender_l or k in body_l:
            return True

    for d in HARD_BLOCK_DOMAINS:
        if d in sender_l:
            return True

    return False


def human_score(sender: str, body: str) -> int:
    score = 0
    sender_l = sender.lower()
    body_l = body.lower()

    # Free email domain = strong human signal
    if any(d in sender_l for d in FREE_EMAIL_DOMAINS):
        score += 3

    # Real name format
    if "<" in sender and ">" in sender:
        score += 2

    # Conversational intent
    if "?" in body_l:
        score += 2

    if any(p in body_l for p in ["i ", "we ", "my ", "our "]):
        score += 2

    if any(p in body_l for p in ["following up", "we discussed", "as mentioned"]):
        score += 2

    # Penalties
    if body_l.count("http") > 2:
        score -= 3

    if len(body_l) > 800:
        score -= 3

    return score


def is_human_email(sender: str, body: str, threshold: int = 3) -> bool:
    if not sender or not body:
        return False

    if is_hard_block(sender, body):
        return False

    score = human_score(sender, body)
    return score >= threshold
