def sainitize_username(username: str) -> str:
    """Remove illegal characters from a username"""
    return re.sub(r'[^a-zA-Z0-9-_@]', "", username)