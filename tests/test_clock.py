from datetime import datetime
from itertools import pairwise

import pytest

from blocky.clock import (
    TimeStyle,
    day_name,
    day_order,
    describe_days,
    describe_schedule,
    format_date,
    format_duration,
    format_hhmm,
    format_time,
    full_day_name,
)

TWELVE = TimeStyle(twelve_hour=True)
SUNDAY_FIRST = TimeStyle(first_day=6)


@pytest.mark.parametrize(
    "hour, minute, text",
    [(0, 0, "12:00 AM"), (0, 30, "12:30 AM"), (1, 5, "1:05 AM"), (11, 59, "11:59 AM"), (12, 0, "12:00 PM"),
     (12, 30, "12:30 PM"), (13, 0, "1:00 PM"), (17, 5, "5:05 PM"), (23, 59, "11:59 PM")],
)  # fmt: skip
def test_twelve_hour_times(hour, minute, text):
    assert format_time(hour, minute, TWELVE) == text


@pytest.mark.parametrize("hour", range(24))
def test_every_hour_in_both_formats(hour):
    assert format_time(hour, 7, TimeStyle()) == f"{hour:02d}:07"
    twelve = format_time(hour, 7, TWELVE)
    shown, period = twelve.split()
    assert period == ("AM" if hour < 12 else "PM")
    assert int(shown.split(":")[0]) in range(1, 13)
    assert int(shown.split(":")[0]) % 12 == hour % 12


def test_stored_time_in_either_format():
    assert format_hhmm("09:00", TimeStyle()) == "09:00"
    assert format_hhmm("17:30", TWELVE) == "5:30 PM"


@pytest.mark.parametrize("first_day", range(7))
def test_day_order_starts_at_the_first_day(first_day):
    order = day_order(TimeStyle(first_day=first_day))
    assert order[0] == first_day
    assert sorted(order) == list(range(7))
    assert all((b - a) % 7 == 1 for a, b in pairwise(order))


@pytest.mark.parametrize(
    "days, monday_first, sunday_first",
    [
        ([0, 1, 2, 3, 4], "Mon–Fri", "Mon–Fri"),
        ([6, 0, 1], "Mon, Tue, Sun", "Sun–Tue"),
        ([5, 6], "Sat, Sun", "Sun, Sat"),
        ([0, 1, 2, 3, 4, 5, 6], "Mon–Sun", "Sun–Sat"),
        ([0, 1, 2, 4, 5, 6], "Mon–Wed, Fri–Sun", "Sun–Wed, Fri, Sat"),
        ([], "no days", "no days"),
        ([3], "Thu", "Thu"),
    ],
)
def test_days_follow_the_first_day(days, monday_first, sunday_first):
    assert describe_days(days, TimeStyle()) == monday_first
    assert describe_days(days, SUNDAY_FIRST) == sunday_first


def test_saturday_first_groups_the_weekend_with_the_week():
    assert describe_days([5, 6, 0], TimeStyle(first_day=5)) == "Sat–Mon"


def test_schedule_description_in_twelve_hour_form():
    assert describe_schedule([0, 1, 2, 3, 4], "09:00", "17:00", TWELVE) == "Mon–Fri, 9:00 AM–5:00 PM"


def test_time_style_cannot_change_in_place():
    # DEFAULT_STYLE is shared as a default argument; changing it would change every caller.
    import dataclasses

    from blocky.clock import DEFAULT_STYLE

    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT_STYLE.twelve_hour = True  # type: ignore[misc]


# Languages

DUTCH = TimeStyle(language="nl")
HUNGARIAN = TimeStyle(language="hu")
SUNDAY_4_OCT_1705 = datetime(2026, 10, 4, 17, 5)


@pytest.mark.parametrize(
    "style, text",
    [
        (TimeStyle(), "Sun 4 Oct 2026, 17:05"),
        (DUTCH, "zo 4 okt 2026, 17:05"),
        (HUNGARIAN, "2026. okt. 4. (V), 17:05"),
        (TimeStyle(twelve_hour=True), "Sun 4 Oct 2026, 5:05 PM"),
        (TimeStyle(twelve_hour=True, language="nl"), "zo 4 okt 2026, 5:05 p.m."),
        (TimeStyle(twelve_hour=True, language="hu"), "2026. okt. 4. (V), du. 5:05"),
    ],
)
def test_history_date_in_each_language(style, text):
    assert format_date(SUNDAY_4_OCT_1705, style) == text


@pytest.mark.parametrize("month", range(1, 13))
def test_every_month_matches_the_c_locale_in_english(month):
    moment = datetime(2026, month, 1, 9, 0)
    assert format_date(moment, TimeStyle()) == f"{moment:%a} 1 {moment:%b %Y}, 09:00"


@pytest.mark.parametrize(
    "code, midnight, noon, evening",
    [
        ("en", "12:00 AM", "12:00 PM", "5:05 PM"),
        ("nl", "12:00 a.m.", "12:00 p.m.", "5:05 p.m."),
        ("hu", "de. 12:00", "du. 12:00", "du. 5:05"),
    ],
)
def test_twelve_hour_markers_in_each_language(code, midnight, noon, evening):
    style = TimeStyle(twelve_hour=True, language=code)
    assert [format_time(0, 0, style), format_time(12, 0, style), format_time(17, 5, style)] == [midnight, noon, evening]


@pytest.mark.parametrize("code", ["en", "nl", "hu"])
def test_24_hour_times_are_the_same_in_every_language(code):
    assert format_time(17, 5, TimeStyle(language=code)) == "17:05"


@pytest.mark.parametrize(
    "code, short, full",
    [
        ("en", "Mon Tue Wed Thu Fri Sat Sun", "Monday Sunday"),
        ("nl", "ma di wo do vr za zo", "maandag zondag"),
        ("hu", "H K Sze Cs P Szo V", "hétfő vasárnap"),
    ],
)
def test_day_names_in_each_language(code, short, full):
    style = TimeStyle(language=code)
    assert " ".join(day_name(day, style) for day in range(7)) == short
    assert f"{full_day_name(0, style)} {full_day_name(6, style)}" == full


@pytest.mark.parametrize(
    "code, text", [("en", "Mon–Fri, 09:00–17:00"), ("nl", "ma–vr, 09:00–17:00"), ("hu", "H–P, 09:00–17:00")]
)
def test_schedule_description_in_each_language(code, text):
    assert describe_schedule([0, 1, 2, 3, 4], "09:00", "17:00", TimeStyle(language=code)) == text


def test_no_days_in_each_language(monkeypatch):
    from blocky import language

    monkeypatch.setitem(language.NL, "no days", "geen dagen")
    assert describe_days([], DUTCH) == "geen dagen"


@pytest.mark.parametrize(
    "code, short, long", [("en", "0h 05m", "12h 30m"), ("nl", "0u 05m", "12u 30m"), ("hu", "0ó 05p", "12ó 30p")]
)
def test_durations_in_each_language(code, short, long):
    assert format_duration(5, code) == short
    assert format_duration(750, code) == long


def test_unknown_language_writes_english():
    style = TimeStyle(twelve_hour=True, language="fr")
    assert format_date(SUNDAY_4_OCT_1705, style) == "Sun 4 Oct 2026, 5:05 PM"
    assert format_duration(65, "fr") == "1h 05m"
