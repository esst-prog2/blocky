from datetime import datetime

import pytest

from blocky import history
from blocky.config import Config, load, save
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
        ([0, 2, 3, 4], "Mon, Wed\u2013Fri"),
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


def test_overrides_read_back_from_the_config_keep_their_labels(tmp_path):
    config = Config(
        overrides=[
            {
                "type": "override",
                "domain": "reddit.com",
                "timestamp": "2026-10-05T14:00:00",
                "until": "2026-10-05T17:00:00",
            },
            {"type": "undo", "domain": "reddit.com", "timestamp": "2026-10-05T14:30:00"},
        ]
    )
    save(tmp_path / "config.yaml", config)
    loaded = load(tmp_path / "config.yaml")
    assert [row.event for row in rows(loaded.events, loaded.overrides)] == ["Override undone", "Override"]


def test_override_saved_without_a_type_is_shown_as_an_override():
    # Blocky's first version wrote overrides without a "type".
    overrides = [{"domain": "reddit.com", "timestamp": "2026-10-05T14:00:00", "reason": "work", "until": "x"}]
    assert [(row.event, row.details) for row in rows([], overrides)] == [("Override", "work")]


# Today's output, captured from history.py before time formats existed; 24-hour time with Monday first must keep it.
WHEN_BEFORE = {
    datetime(2026, 10, 5, 14, 0): "Mon 5 Oct 2026, 14:00",
    datetime(2026, 1, 4, 0, 5): "Sun 4 Jan 2026, 00:05",
    datetime(2026, 12, 31, 23, 59): "Thu 31 Dec 2026, 23:59",
    datetime(2026, 10, 11, 9, 7): "Sun 11 Oct 2026, 09:07",
}
DAYS_BEFORE = [
    ([0, 1, 2, 3, 4], "Mon–Fri"),
    ([0, 2, 4], "Mon, Wed, Fri"),
    ([5, 6], "Sat, Sun"),
    ([0, 1, 6], "Mon, Tue, Sun"),
    ([6, 0, 1], "Mon, Tue, Sun"),
    ([], "no days"),
    ([0, 1, 2, 3, 4, 5, 6], "Mon–Sun"),
    ([1, 2], "Tue, Wed"),
    ([0, 1, 2, 4, 5, 6], "Mon–Wed, Fri–Sun"),
    ([3], "Thu"),
]


def test_default_style_keeps_todays_output():
    assert {moment: history.when(moment) for moment in WHEN_BEFORE} == WHEN_BEFORE
    assert [(days, history.describe_days(days)) for days, _ in DAYS_BEFORE] == DAYS_BEFORE
    assert history.describe_schedule([0, 1, 2, 3, 4], "09:00", "17:00") == "Mon–Fri, 09:00–17:00"
