from datetime import datetime

import pytest

from blocky.schedule import Schedule, parse_time, validate, window_end

MONDAY = 5  # 2026-10-05
SATURDAY = 10  # 2026-10-10


def at(day, hour, minute):
    return datetime(2026, 10, day, hour, minute)


def test_inside_window_returns_end_of_window():
    assert window_end(Schedule(), at(MONDAY, 14, 0)) == at(MONDAY, 17, 0)


def test_start_time_is_inside_window():
    assert window_end(Schedule(), at(MONDAY, 9, 0)) == at(MONDAY, 17, 0)


def test_end_time_is_outside_window():
    assert window_end(Schedule(), at(MONDAY, 17, 0)) is None


def test_minute_before_start_is_outside_window():
    assert window_end(Schedule(), at(MONDAY, 8, 59)) is None


def test_unselected_weekday_is_outside_window():
    assert window_end(Schedule(), at(SATURDAY, 14, 0)) is None


def test_start_must_be_before_end():
    with pytest.raises(ValueError):
        validate(Schedule(start="17:00", end="09:00"))


def test_weekday_must_be_in_range():
    with pytest.raises(ValueError):
        validate(Schedule(weekdays=[7]))


@pytest.mark.parametrize("text, stored", [("9:00", "09:00"), ("09:00", "09:00"), (" 17:30 ", "17:30"), ("0:05", "00:05")])
def test_time_is_accepted_as_hours_and_minutes(text, stored):
    assert parse_time(text) == stored


@pytest.mark.parametrize("text", ["nine", "24:00", "9:60", "0900", "9", "09:00:30", ""])
def test_other_time_text_is_rejected_with_a_clear_message(text):
    with pytest.raises(ValueError, match="Use a time like 09:00"):
        parse_time(text)
