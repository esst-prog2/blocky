"""Clock times and weekdays as text, in the user's time format and with their first day of the week."""

from dataclasses import dataclass

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # weekday numbers 0 (Monday) to 6 (Sunday)


@dataclass(frozen=True)
class TimeStyle:
    twelve_hour: bool = False
    first_day: int = 0  # a weekday number, as stored in the schedule


DEFAULT_STYLE = TimeStyle()  # 24-hour, Monday first: Blocky before these settings existed


def format_time(hour: int, minute: int, style: TimeStyle) -> str:
    """'17:05' or '5:05 PM'; no leading zero in 12-hour form, as Windows writes it."""
    if not style.twelve_hour:
        return f"{hour:02d}:{minute:02d}"
    return f"{(hour - 1) % 12 + 1}:{minute:02d} {'AM' if hour < 12 else 'PM'}"


def format_hhmm(text: str, style: TimeStyle) -> str:
    """A stored 'HH:MM' time in the user's format."""
    hour, minute = text.split(":")
    return format_time(int(hour), int(minute), style)


def day_order(style: TimeStyle) -> list[int]:
    """The seven weekday numbers, starting at the first day of the week."""
    return [(style.first_day + offset) % 7 for offset in range(7)]


def describe_days(weekdays: list[int], style: TimeStyle) -> str:
    """The days in week order; three or more that follow each other become one range, from the first to the last."""
    chosen = set(weekdays)
    if not chosen:
        return "no days"
    runs: list[list[int]] = []
    previous: int | None = None
    for position, day in enumerate(day_order(style)):
        if day not in chosen:
            continue
        if runs and previous == position - 1:
            runs[-1].append(day)
        else:
            runs.append([day])
        previous = position
    parts = []
    for run in runs:
        if len(run) >= 3:
            parts.append(f"{DAY_NAMES[run[0]]}–{DAY_NAMES[run[-1]]}")
        else:
            parts.extend(DAY_NAMES[day] for day in run)
    return ", ".join(parts)


def describe_schedule(weekdays: list[int], start: str, end: str, style: TimeStyle) -> str:
    return f"{describe_days(weekdays, style)}, {format_hhmm(start, style)}–{format_hhmm(end, style)}"
