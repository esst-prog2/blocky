from dataclasses import dataclass
from datetime import datetime

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

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


def when(moment: datetime) -> str:
    return f"{moment:%a} {moment.day} {moment:%b %Y, %H:%M}"


def describe_days(weekdays: list[int]) -> str:
    days = sorted(set(weekdays))
    if not days:
        return "no days"
    runs: list[list[int]] = []
    for day in days:
        if runs and day == runs[-1][-1] + 1:
            runs[-1].append(day)
        else:
            runs.append([day])
    parts = []
    for run in runs:
        if len(run) >= 3:
            parts.append(f"{DAY_NAMES[run[0]]}–{DAY_NAMES[run[-1]]}")
        else:
            parts.extend(DAY_NAMES[day] for day in run)
    return ", ".join(parts)


def describe_schedule(weekdays: list[int], start: str, end: str) -> str:
    return f"{describe_days(weekdays)}, {start}–{end}"


def rows(events: list[dict], overrides: list[dict]) -> list[Row]:
    """All recorded changes, newest first."""
    found = [
        (datetime.fromisoformat(entry["timestamp"]), EVENTS.get(entry["type"], entry["type"]),
         entry.get("item", ""), entry.get("details", ""))
        for entry in events
    ]
    for entry in overrides:
        undo = entry.get("type") == "undo"
        found.append((
            datetime.fromisoformat(entry["timestamp"]),
            EVENTS["undo" if undo else "override"],
            entry["domain"],
            "" if undo else entry.get("reason", ""),
        ))
    ordered = sorted(enumerate(found), key=lambda pair: (pair[1][0], pair[0]), reverse=True)
    return [Row(*row) for _, row in ordered]
