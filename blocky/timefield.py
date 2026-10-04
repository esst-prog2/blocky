from datetime import time

import customtkinter as ctk

from blocky import theme


def digits(text: str) -> bool:
    """Whether the text is only the digits 0-9; str.isdigit() also accepts characters like '²' that int() rejects."""
    return text.isascii() and text.isdigit()


def allowed(text: str, maximum: int) -> bool:
    """Whether a box may hold this text while the user types: at most two digits, not above the maximum."""
    return text == "" or (digits(text) and len(text) <= 2 and int(text) <= maximum)


def step(text: str, delta: int, maximum: int, minimum: int = 0, pad: bool = True) -> str:
    """The value one step up or down, wrapping from the maximum back to the minimum and the other way round."""
    value = int(text) if digits(text) else minimum
    stepped = minimum + (value - minimum + delta) % (maximum - minimum + 1)
    return f"{stepped:02d}" if pad else str(stepped)


def finish(text: str, previous: str, minimum: int = 0, pad: bool = True) -> str:
    """The value a box settles on when the user leaves it: padded, or the previous value if empty or too low."""
    if not digits(text) or int(text) < minimum:
        return previous
    return f"{int(text):02d}" if pad else str(int(text))


def to_twelve_hour(hour: int) -> tuple[int, bool]:
    """A 24-hour hour as an hour from 1 to 12 and whether it is PM: 0 is 12 AM, 12 is 12 PM."""
    return (hour - 1) % 12 + 1, hour >= 12


def to_24_hour(hour: int, pm: bool) -> int:
    return hour % 12 + (12 if pm else 0)


class _Box(ctk.CTkEntry):
    def __init__(self, parent: ctk.CTkFrame, value: int, maximum: int, minimum: int = 0, pad: bool = True) -> None:
        super().__init__(parent, justify="center", **{**theme.entry_style(), "width": theme.px(48)})
        self.maximum = maximum
        self.minimum = minimum
        self.pad = pad
        self.settled = f"{value:02d}" if pad else str(value)
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
        self.settled = step(self.get(), delta, self.maximum, self.minimum, self.pad)
        self._set(self.settled)
        return "break"

    def settle(self) -> str:
        self.settled = finish(self.get(), self.settled, self.minimum, self.pad)
        self._set(self.settled)
        return self.settled


class TimeField(ctk.CTkFrame):
    """An HH : MM time input that only ever holds a valid time; in 12-hour form an hour from 1 to 12 and AM/PM."""

    def __init__(
        self, parent: ctk.CTkFrame, value: str, twelve_hour: bool = False, periods: tuple[str, str] = ("AM", "PM")
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        saved = time.fromisoformat(value)
        self.twelve_hour = twelve_hour
        self.periods = periods  # the markers for before and after noon, in the user's language
        if twelve_hour:
            hour, pm = to_twelve_hour(saved.hour)
            self.hour = _Box(self, hour, 12, minimum=1, pad=False)
        else:
            self.hour = _Box(self, saved.hour, 23)
        self.hour.pack(side="left")
        theme.label(self, ":", "title", theme.MUTED, width=theme.px(14), anchor="center").pack(side="left", padx=2)
        self.minute = _Box(self, saved.minute, 59)
        self.minute.pack(side="left")
        self.period: ctk.CTkSegmentedButton | None = None
        if twelve_hour:
            self.period = ctk.CTkSegmentedButton(
                self,
                values=list(periods),
                font=theme.font("button"),
                height=theme.CONTROL_HEIGHT,
                corner_radius=8,
                fg_color=theme.CARD,
                selected_color=theme.DEEP,
                selected_hover_color=theme.DEEP,
                unselected_color=theme.BACKGROUND,
                unselected_hover_color=theme.HOVER,
                text_color=theme.ON_DEEP,
            )
            self.period.set(periods[pm])
            self.period.pack(side="left", padx=(theme.GAP, 0))

    def get(self) -> str:
        """The time as stored: 24-hour 'HH:MM'."""
        hour = int(self.hour.settle())
        if self.period is not None:
            hour = to_24_hour(hour, self.period.get() == self.periods[1])
        return f"{hour:02d}:{self.minute.settle()}"
