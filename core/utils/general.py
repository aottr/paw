import re

def sanitize_username(username: str) -> str:
    """Remove illegal characters from a username: allow [a-zA-Z0-9-_@]."""
    return re.sub(r"[^a-zA-Z0-9-_@]", "", username or "")