from datetime import datetime

import pytest

from blocky.history import describe_days, describe_schedule, rows, when


def test_dates_are_readable():
    assert when(datetime(2026, 10, 5, 14, 0)) == "Mon 5 Oct 2026, 14:00"


@pytest.mark.parametrize(
    "days, text",
    [
        ([0, 1, 2, 3, 4], "Mon\u2013Fri"),
        ([0, 1, 2, 3, 4, 5, 6], "Mon\u2013Sun"),
        ([0, 2, 4], "Mon, Wed, Fri"),
        ([5, 6], "Sat, Sun"),
        ([0, 1, 2, 5], "Mon\u2013Wed, Sat"),
        ([], "no days"),
    ],
)
def test_days_are_described_compactly(days, text):
    assert describe_days(days) == text


def test_schedule_description():
    assert describe_schedule([0, 1, 2, 3, 4], "09:00", "17:00") == "Mon\u2013Fri, 09:00\u201317:00"


def test_events_and_overrides_are_merged_newest_first():
    events = [{"type": "site_added", "timestamp": "2026-10-05T13:00:00", "item": "reddit.com", "details": ""}]
    overrides = [
        {
            "type": "override",
            "domain": "reddit.com",
            "timestamp": "2026-10-05T14:00:00",
            "reason": "work",
            "until": "2026-10-05T17:00:00",
        },
        {"type": "undo", "domain": "reddit.com", "timestamp": "2026-10-05T14:30:00"},
    ]
    assert [(row.event, row.details) for row in rows(events, overrides)] == [
        ("Override undone", ""),
        ("Override", "work"),
        ("Site added", ""),
    ]
