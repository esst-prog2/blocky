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


def rows(events: list[dict], overrides: list[dict]) -> list[Row]:
    """All recorded changes, newest first."""
    found = [
        (
            datetime.fromisoformat(entry["timestamp"]),
            EVENTS.get(entry["type"], entry["type"]),
            entry.get("item", ""),
            entry.get("details", ""),
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
