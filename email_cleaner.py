import re

SIGNATURE_PATTERNS = [
    r"sent from my .*",
    r"best regards.*",
    r"regards.*",
    r"thanks.*",
    r"sincerely.*",
    r"kind regards.*",
    r"--\s*\n.*"
]

REPLY_PATTERNS = [
    r"on .* wrote:",
    r"from:.*",
    r"to:.*",
    r"subject:.*",
    r">.*"
]

UNICODE_JUNK = [
    "\u2007",
    "\u200b",
    "\xad",
    "\ufeff"
]


def clean_email(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # Remove unicode junk
    for char in UNICODE_JUNK:
        text = text.replace(char, "")

    # Remove reply chains
    for pattern in REPLY_PATTERNS:
        text = re.split(pattern, text, flags=re.IGNORECASE)[0]

    # Remove signatures
    for pattern in SIGNATURE_PATTERNS:
        text = re.split(pattern, text, flags=re.IGNORECASE)[0]

    # Normalize whitespace
    text = re.sub(r"\n{2,}", "\n", text)
    text = text.strip()

    return text
