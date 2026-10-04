from itertools import pairwise

import pytest

from blocky.clock import TimeStyle, day_order, describe_days, describe_schedule, format_hhmm, format_time

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
