from datetime import time

import customtkinter as ctk

from blocky import theme


def allowed(text: str, maximum: int) -> bool:
    """Whether a box may hold this text while the user types: at most two digits, not above the maximum."""
    return text == "" or (text.isdigit() and len(text) <= 2 and int(text) <= maximum)


def step(text: str, delta: int, maximum: int) -> str:
    value = int(text) if text.isdigit() else 0
    return f"{(value + delta) % (maximum + 1):02d}"


def finish(text: str, previous: str) -> str:
    """The value a box settles on when the user leaves it: padded, or the previous value if left empty."""
    return f"{int(text):02d}" if text.isdigit() else previous


class _Box(ctk.CTkEntry):
    def __init__(self, parent: ctk.CTkFrame, value: int, maximum: int) -> None:
        super().__init__(parent, justify="center", **{**theme.entry_style(), "width": 48})
        self.maximum = maximum
        self.settled = f"{value:02d}"
        self.insert(0, self.settled)
        self.configure(validate="key", validatecommand=(self.register(self._allowed), "%P"))
        self.bind("<Up>", lambda _event: self._step(1))
        self.bind("<Down>", lambda _event: self._step(-1))
        self.bind("<MouseWheel>", lambda event: self._step(1 if event.delta > 0 else -1))
        self.bind("<FocusOut>", lambda _event: self.settle())

    def _allowed(self, text: str) -> bool:
        return allowed(text, self.maximum)

    def _set(self, text: str) -> None:
        self.delete(0, "end")
        self.insert(0, text)

    def _step(self, delta: int) -> str:
        self.settled = step(self.get(), delta, self.maximum)
        self._set(self.settled)
        return "break"

    def settle(self) -> str:
        self.settled = finish(self.get(), self.settled)
        self._set(self.settled)
        return self.settled


class TimeField(ctk.CTkFrame):
    """An HH : MM time input that only ever holds a valid time."""

    def __init__(self, parent: ctk.CTkFrame, value: str) -> None:
        super().__init__(parent, fg_color="transparent")
        saved = time.fromisoformat(value)
        self.hour = _Box(self, saved.hour, 23)
        self.hour.pack(side="left")
        theme.label(self, ":", "title", theme.MUTED, width=14, anchor="center").pack(side="left", padx=2)
        self.minute = _Box(self, saved.minute, 59)
        self.minute.pack(side="left")

    def get(self) -> str:
        return f"{self.hour.settle()}:{self.minute.settle()}"
