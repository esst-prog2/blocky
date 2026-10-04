import re
from dataclasses import dataclass
from datetime import datetime

from blocky import clock, language
from blocky.clock import DEFAULT_STYLE, TimeStyle
from blocky.language import marked

# Event names in English; History shows them in the language of the style it is given.
EVENTS = {
    "site_added": marked("Site added", context="event"),
    "site_edited": marked("Site edited", context="event"),
    "site_removed": marked("Site removed", context="event"),
    "suggestion_added": marked("Suggestion added", context="event"),
    "suggestion_edited": marked("Suggestion edited", context="event"),
    "suggestion_removed": marked("Suggestion removed", context="event"),
    "schedule_changed": marked("Schedule changed", context="event"),
    "override": marked("Override", context="event"),
    "undo": marked("Override undone", context="event"),
}


@dataclass
class Row:
    moment: datetime
    event: str
    item: str
    details: str
    kind: str = ""  # the stored event type, such as "override"


def when(moment: datetime, style: TimeStyle = DEFAULT_STYLE) -> str:
    return clock.format_date(moment, style)


def describe_days(weekdays: list[int], style: TimeStyle = DEFAULT_STYLE) -> str:
    return clock.describe_days(weekdays, style)


def describe_schedule(weekdays: list[int], start: str, end: str, style: TimeStyle = DEFAULT_STYLE) -> str:
    return clock.describe_schedule(weekdays, start, end, style)


_DAY_NUMBERS = {name: number for number, name in enumerate(clock.DAY_NAMES)}
_SCHEDULE_TEXT = re.compile(r"(?P<days>.+), (?P<start>[0-9]{2}:[0-9]{2})–(?P<end>[0-9]{2}:[0-9]{2})")


def _days_from_text(text: str) -> list[int] | None:
    if text == "no days":
        return []
    days: list[int] = []
    for part in text.split(", "):
        first, _, last = part.partition("–")
        if first not in _DAY_NUMBERS or (last and last not in _DAY_NUMBERS):
            return None
        days.extend(range(_DAY_NUMBERS[first], _DAY_NUMBERS[last or first] + 1))
    return days


def _valid_time(text: object) -> bool:
    return isinstance(text, str) and re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", text) is not None


def schedule_parts(entry: dict) -> tuple[list[int], str, str] | None:
    """The days and times of a schedule change: stored as fields, or read from the text earlier versions stored.

    Text is only read when describing what was read gives back exactly that text, so nothing is ever misread.
    """
    weekdays, start, end = entry.get("weekdays"), entry.get("start"), entry.get("end")
    if (
        isinstance(weekdays, list)
        and all(isinstance(day, int) and day in range(7) for day in weekdays)
        and _valid_time(start)
        and _valid_time(end)
    ):
        return weekdays, start, end  # type: ignore[return-value]
    match = _SCHEDULE_TEXT.fullmatch(str(entry.get("details", "")))
    if not match or not _valid_time(match["start"]) or not _valid_time(match["end"]):
        return None
    days = _days_from_text(match["days"])
    if days is None or describe_schedule(days, match["start"], match["end"]) != match[0]:
        return None
    return days, match["start"], match["end"]


def _details(entry: dict, style: TimeStyle) -> str:
    if entry["type"] == "schedule_changed":
        parts = schedule_parts(entry)
        if parts is not None:
            return describe_schedule(*parts, style)
    return entry.get("details", "")


def _event_name(kind: str, style: TimeStyle) -> str:
    """The event's name in the style's language; an unknown type is shown as stored."""
    return language.translate(EVENTS[kind], style.language, context="event") if kind in EVENTS else kind


def rows(events: list[dict], overrides: list[dict], style: TimeStyle = DEFAULT_STYLE) -> list[Row]:
    """All recorded changes, newest first, with names and schedule details in the given time style."""
    found = [
        (
            datetime.fromisoformat(entry["timestamp"]),
            _event_name(entry["type"], style),
            entry.get("item", ""),
            _details(entry, style),
            entry["type"],
        )
        for entry in events
    ]
    for entry in overrides:
        kind = "undo" if entry.get("type") == "undo" else "override"
        found.append(
            (
                datetime.fromisoformat(entry["timestamp"]),
                _event_name(kind, style),
                entry["domain"],
                "" if kind == "undo" else entry.get("reason", ""),
                kind,
            )
        )
    ordered = sorted(enumerate(found), key=lambda pair: (pair[1][0], pair[0]), reverse=True)
    return [Row(*row) for _, row in ordered]
