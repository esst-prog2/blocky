from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from blocky import history
from blocky.clock import DEFAULT_STYLE, TimeStyle
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


# Schedule details follow the time style


TWELVE_SUNDAY = TimeStyle(twelve_hour=True, first_day=6)


def schedule_event(**fields):
    return {"type": "schedule_changed", "timestamp": "2026-10-05T13:00:00", "item": "", **fields}


def details(entry, style):
    return rows([entry], [], style)[0].details


def test_new_schedule_events_are_shown_in_the_style():
    entry = schedule_event(details="Mon, Tue, Sun, 09:00–17:30", weekdays=[0, 1, 6], start="09:00", end="17:30")
    assert details(entry, DEFAULT_STYLE) == "Mon, Tue, Sun, 09:00–17:30"
    assert details(entry, TWELVE_SUNDAY) == "Sun–Tue, 9:00 AM–5:30 PM"


def test_fields_win_over_the_stored_text():
    entry = schedule_event(details="something older", weekdays=[0, 1, 2, 3, 4], start="08:00", end="12:00")
    assert details(entry, DEFAULT_STYLE) == "Mon–Fri, 08:00–12:00"


@pytest.mark.parametrize(
    "text, twelve_sunday",
    [
        ("Mon–Fri, 09:00–17:00", "Mon–Fri, 9:00 AM–5:00 PM"),
        ("Mon, Tue, Sun, 08:30–16:00", "Sun–Tue, 8:30 AM–4:00 PM"),
        ("Mon–Wed, Fri–Sun, 00:00–12:00", "Sun–Wed, Fri, Sat, 12:00 AM–12:00 PM"),
        ("no days, 09:00–17:00", "no days, 9:00 AM–5:00 PM"),
    ],
)
def test_older_text_in_the_known_pattern_is_shown_in_the_style(text, twelve_sunday):
    entry = schedule_event(details=text)
    assert details(entry, DEFAULT_STYLE) == text
    assert details(entry, TWELVE_SUNDAY) == twelve_sunday


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Mon to Fri, 9 till 5",
        "Mon–Fri, 9:00–17:00",  # not the pattern earlier versions wrote
        "Mon, Tue, Wed, 09:00–17:00",  # earlier versions grouped these three days into one range
        "Fri–Mon, 09:00–17:00",
        "Mon–Fri, 25:00–26:00",
        "Funday, 09:00–17:00",
    ],
)
def test_other_text_is_shown_as_stored(text):
    assert details(schedule_event(details=text), TWELVE_SUNDAY) == text


def test_broken_fields_fall_back_to_the_text():
    entry = schedule_event(details="Mon–Fri, 09:00–17:00", weekdays=[0, 9], start="09:00", end="17:00")
    assert details(entry, TWELVE_SUNDAY) == "Mon–Fri, 9:00 AM–5:00 PM"
    assert details(schedule_event(details="kept", weekdays="Mon", start=9, end=None), TWELVE_SUNDAY) == "kept"


def test_other_events_keep_their_details():
    entry = {"type": "site_edited", "timestamp": "2026-10-05T13:00:00", "item": "x.com", "details": "a.com → x.com"}
    assert details(entry, TWELVE_SUNDAY) == "a.com → x.com"


@given(st.text())
def test_any_text_reformats_to_the_same_schedule_or_comes_back_unchanged(text):
    parts = history.schedule_parts(schedule_event(details=text))
    if parts is None:
        assert details(schedule_event(details=text), TWELVE_SUNDAY) == text
    else:
        assert history.describe_schedule(*parts) == text


@given(st.sets(st.integers(0, 6)), st.integers(0, 23), st.integers(0, 59), st.integers(0, 23), st.integers(0, 59))
def test_every_text_earlier_versions_wrote_is_read_back(days, h1, m1, h2, m2):
    start, end = f"{h1:02d}:{m1:02d}", f"{h2:02d}:{m2:02d}"
    text = history.describe_schedule(sorted(days), start, end)
    assert history.schedule_parts(schedule_event(details=text)) == (sorted(days), start, end)


# Languages: stored text stays English, shown text follows the language


@pytest.mark.parametrize(
    "code, text", [("en", "Mon–Fri, 09:00–17:00"), ("nl", "ma–vr, 09:00–17:00"), ("hu", "H–P, 09:00–17:00")]
)
def test_older_english_text_is_shown_in_the_language(code, text):
    entry = schedule_event(details="Mon–Fri, 09:00–17:00")
    assert details(entry, TimeStyle(language=code)) == text


def test_new_schedule_events_are_shown_in_the_language():
    entry = schedule_event(details="Mon, Tue, Sun, 09:00–17:30", weekdays=[0, 1, 6], start="09:00", end="17:30")
    assert details(entry, TimeStyle(twelve_hour=True, first_day=6, language="hu")) == "V–K, de. 9:00–du. 5:30"


@pytest.mark.parametrize("code", ["nl", "hu"])
def test_details_stored_for_a_new_schedule_are_english_whatever_the_language(tmp_path, code):
    from blocky import language
    from blocky.controller import Controller

    language.apply(code)
    controller = Controller(tmp_path / "config.yaml", tmp_path / "hosts", clock=lambda: datetime(2026, 10, 5, 14))
    controller.sync = lambda: None
    controller.set_schedule([0, 2, 4], "08:30", "16:00")
    assert controller.config.events[-1]["details"] == "Mon, Wed, Fri, 08:30–16:00"
    assert load(tmp_path / "config.yaml").events[-1]["details"] == "Mon, Wed, Fri, 08:30–16:00"
