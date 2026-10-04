import re
from dataclasses import dataclass
from datetime import datetime

from blocky import clock
from blocky.clock import DEFAULT_STYLE, TimeStyle, format_time

EVENTS = {
    "site_added": "Site added",
    "site_edited": "Site edited",
    "site_removed": "Site removed",
    "suggestion_added": "Suggestion added",
    "suggestion_edited": "Suggestion edited",
    "suggestion_removed": "Suggestion removed",
    "schedule_changed": "Schedule changed",
    "override": "Override",
    "undo": "Override undone",
}


@dataclass
class Row:
    moment: datetime
    event: str
    item: str
    details: str


def when(moment: datetime, style: TimeStyle = DEFAULT_STYLE) -> str:
    return f"{moment:%a} {moment.day} {moment:%b %Y}, {format_time(moment.hour, moment.minute, style)}"


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


def rows(events: list[dict], overrides: list[dict], style: TimeStyle = DEFAULT_STYLE) -> list[Row]:
    """All recorded changes, newest first, with schedule details in the given time style."""
    found = [
        (
            datetime.fromisoformat(entry["timestamp"]),
            EVENTS.get(entry["type"], entry["type"]),
            entry.get("item", ""),
            _details(entry, style),
        )
        for entry in events
    ]
    for entry in overrides:
        undo = entry.get("type") == "undo"
        found.append(
            (
                datetime.fromisoformat(entry["timestamp"]),
                EVENTS["undo" if undo else "override"],
                entry["domain"],
                "" if undo else entry.get("reason", ""),
            )
        )
    ordered = sorted(enumerate(found), key=lambda pair: (pair[1][0], pair[0]), reverse=True)
    return [Row(*row) for _, row in ordered]
