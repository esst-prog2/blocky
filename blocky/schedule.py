from dataclasses import dataclass, field
from datetime import datetime, time


@dataclass
class Schedule:
    weekdays: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    start: str = "09:00"
    end: str = "17:00"


def validate(schedule: Schedule) -> None:
    start = time.fromisoformat(schedule.start)
    end = time.fromisoformat(schedule.end)
    if not start < end:
        raise ValueError("The start time must be before the end time")
    if not all(day in range(7) for day in schedule.weekdays):
        raise ValueError("Weekdays must be between 0 (Monday) and 6 (Sunday)")


def window_end(schedule: Schedule, now: datetime) -> datetime | None:
    if now.weekday() not in schedule.weekdays:
        return None
    start = time.fromisoformat(schedule.start)
    end = time.fromisoformat(schedule.end)
    if not start <= now.time() < end:
        return None
    return now.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
