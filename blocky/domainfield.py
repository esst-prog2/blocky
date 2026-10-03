import tkinter
from collections.abc import Callable

import customtkinter as ctk

from blocky.domains import covered_hostnames, host_of, validate

DOMAIN_CHARACTERS = set("abcdefghijklmnopqrstuvwxyz0123456789-.")
MAX_LENGTH = 253


def allowed(text: str) -> bool:
    """Whether a domain box may hold this text while the user types."""
    return len(text) <= MAX_LENGTH and all(character in DOMAIN_CHARACTERS for character in text.lower())


def cleaned_paste(text: str) -> str:
    """What a pasted text becomes: a web address is reduced to its domain, other characters are dropped."""
    host = host_of(text)
    return "".join(character for character in host if character in DOMAIN_CHARACTERS)[:MAX_LENGTH]


def hint(text: str, existing: list[str]) -> tuple[bool, str]:
    """Whether the text can be added, and the line to show under the box."""
    if not text.strip():
        return False, ""
    try:
        domain = validate(text)
    except ValueError:
        return False, "Not a full domain yet, e.g. reddit.com"
    if domain in existing:
        return False, f"{domain} is already in the list"
    return True, "Adds " + " and ".join(covered_hostnames(domain))


class DomainField(ctk.CTkEntry):
    """A text box that only accepts characters that can appear in a domain."""

    def __init__(self, parent: ctk.CTkFrame, on_change: Callable[[], None] = lambda: None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.configure(validate="key", validatecommand=(self.register(allowed), "%P"))
        self.bind("<<Paste>>", self._paste)
        self.bind("<KeyRelease>", lambda _event: self.on_change())

    def paste_text(self, text: str) -> None:
        try:
            self.delete("sel.first", "sel.last")
        except tkinter.TclError:
            pass  # nothing selected
        self.insert("insert", cleaned_paste(text))
        self.on_change()

    def _paste(self, _event: object) -> str:
        try:
            self.paste_text(self.clipboard_get())
        except tkinter.TclError:
            pass  # clipboard empty or not text
        return "break"
