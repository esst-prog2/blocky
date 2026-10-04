from blocky.language import _

MAX_LENGTH = 120


def check(text: str, existing: list[str], original: str | None = None) -> str:
    """Return the suggestion as it will be stored, or raise ValueError saying why it cannot be."""
    cleaned = " ".join(text.split())
    if not cleaned:
        raise ValueError(_("Type a suggestion"))
    if len(cleaned) > MAX_LENGTH:
        raise ValueError(_("Keep it to {count} characters", count=MAX_LENGTH))
    others = [item.lower() for item in existing if item != original]
    if cleaned.lower() in others:
        raise ValueError(_("“{text}” is already in the list", text=cleaned))
    return cleaned


def hint(text: str, existing: list[str]) -> tuple[bool, str]:
    """Whether the text can be added, and the line to show under the box."""
    if not text.strip():
        return False, ""
    try:
        check(text, existing)
    except ValueError as problem:
        return False, str(problem)
    return True, ""


def can_save_edit(text: str, original: str, existing: list[str]) -> bool:
    try:
        return check(text, existing, original) != original
    except ValueError:
        return False
