"""Clock times, dates and weekdays as text, in the user's language, time format and first day of the week."""

from dataclasses import dataclass
from datetime import datetime

from blocky import language

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # weekday numbers 0 (Monday) to 6 (Sunday)

# Per language: short and full weekday names (Monday first), short month names, the before- and after-noon markers
# and whether they come before the time, the History date and the units of a duration.
SHORT_DAYS = {
    "en": DAY_NAMES,
    "nl": ["ma", "di", "wo", "do", "vr", "za", "zo"],
    "hu": ["H", "K", "Sze", "Cs", "P", "Szo", "V"],
}
FULL_DAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "nl": ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"],
    "hu": ["hétfő", "kedd", "szerda", "csütörtök", "péntek", "szombat", "vasárnap"],
}
MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "nl": ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
    "hu": ["jan.", "febr.", "márc.", "ápr.", "máj.", "jún.", "júl.", "aug.", "szept.", "okt.", "nov.", "dec."],
}
PERIODS = {"en": ("AM", "PM"), "nl": ("a.m.", "p.m."), "hu": ("de.", "du.")}
PERIOD_FIRST = {"en": False, "nl": False, "hu": True}
DATES = {
    "en": "{weekday} {day} {month} {year}, {time}",
    "nl": "{weekday} {day} {month} {year}, {time}",
    "hu": "{year}. {month} {day}. ({weekday}), {time}",
}
DURATIONS = {"en": "{hours}h {minutes:02d}m", "nl": "{hours}u {minutes:02d}m", "hu": "{hours}ó {minutes:02d}p"}


@dataclass(frozen=True)
class TimeStyle:
    twelve_hour: bool = False
    first_day: int = 0  # a weekday number, as stored in the schedule
    language: str = "en"


DEFAULT_STYLE = TimeStyle()  # English, 24-hour, Monday first: Blocky before these settings existed


def _code(style: TimeStyle) -> str:
    return style.language if style.language in language.LANGUAGES else "en"


def periods(style: TimeStyle) -> tuple[str, str]:
    """The markers for before and after noon in the style's language."""
    return PERIODS[_code(style)]


def format_time(hour: int, minute: int, style: TimeStyle) -> str:
    """'17:05', or in 12-hour form '5:05 PM' (English), '5:05 p.m.' (Dutch) or 'du. 5:05' (Hungarian).

    No leading zero in 12-hour form, as Windows writes it.
    """
    if not style.twelve_hour:
        return f"{hour:02d}:{minute:02d}"
    clock = f"{(hour - 1) % 12 + 1}:{minute:02d}"
    period = periods(style)[hour >= 12]
    return f"{period} {clock}" if PERIOD_FIRST[_code(style)] else f"{clock} {period}"


def format_hhmm(text: str, style: TimeStyle) -> str:
    """A stored 'HH:MM' time in the user's format."""
    hour, minute = text.split(":")
    return format_time(int(hour), int(minute), style)


def format_date(moment: datetime, style: TimeStyle) -> str:
    """A History date and time: 'Sun 4 Oct 2026, 17:05', 'zo 4 okt 2026, 17:05' or '2026. okt. 4. (V), 17:05'."""
    code = _code(style)
    return DATES[code].format(
        weekday=SHORT_DAYS[code][moment.weekday()],
        day=moment.day,
        month=MONTHS[code][moment.month - 1],
        year=moment.year,
        time=format_time(moment.hour, moment.minute, style),
    )


def format_duration(minutes: int, code: str) -> str:
    """Hours and minutes in the language's units: '2h 05m', '2u 05m' or '2ó 05p'."""
    units = DURATIONS.get(code, DURATIONS["en"])
    return units.format(hours=minutes // 60, minutes=minutes % 60)


def day_name(day: int, style: TimeStyle) -> str:
    return SHORT_DAYS[_code(style)][day]


def full_day_name(day: int, style: TimeStyle) -> str:
    return FULL_DAYS[_code(style)][day]


def day_order(style: TimeStyle) -> list[int]:
    """The seven weekday numbers, starting at the first day of the week."""
    return [(style.first_day + offset) % 7 for offset in range(7)]


def describe_days(weekdays: list[int], style: TimeStyle) -> str:
    """The days in week order; three or more that follow each other become one range, from the first to the last."""
    chosen = set(weekdays)
    if not chosen:
        return language.translate("no days", _code(style))
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
            parts.append(f"{day_name(run[0], style)}–{day_name(run[-1], style)}")
        else:
            parts.extend(day_name(day, style) for day in run)
    return ", ".join(parts)


def describe_schedule(weekdays: list[int], start: str, end: str, style: TimeStyle) -> str:
    return f"{describe_days(weekdays, style)}, {format_hhmm(start, style)}–{format_hhmm(end, style)}"
