from datetime import datetime

import pytest

from blocky import config as config_module
from blocky import rules
from blocky.controller import Controller, warning_text
from blocky.server import render_blocked

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)


@pytest.fixture
def make(tmp_path):
    clock = {"now": MONDAY_2PM}

    def factory():
        return Controller(
            tmp_path / "config.yaml",
            tmp_path / "hosts",
            clock=lambda: clock["now"],
        )

    factory.clock = clock  # type: ignore[attr-defined]
    factory.path = tmp_path / "config.yaml"  # type: ignore[attr-defined]
    return factory


def test_add_edit_remove_domain(make):
    controller = make()
    controller.add_domain("reddit.com")
    assert controller.config.domains == ["reddit.com"]
    controller.edit_domain(0, "youtube.com")
    assert controller.config.domains == ["youtube.com"]
    controller.remove_domain(0)
    assert controller.config.domains == []


def test_invalid_domain_is_rejected_and_list_unchanged(make):
    controller = make()
    with pytest.raises(ValueError):
        controller.add_domain("reddit")
    assert controller.config.domains == []


def test_duplicate_domain_is_rejected(make):
    controller = make()
    controller.add_domain("reddit.com")
    with pytest.raises(ValueError):
        controller.add_domain("reddit.com")
    assert controller.config.domains == ["reddit.com"]


def test_editing_into_a_duplicate_is_rejected(make):
    controller = make()
    controller.add_domain("reddit.com")
    controller.add_domain("chess.com")
    with pytest.raises(ValueError):
        controller.edit_domain(1, "reddit.com")
    with pytest.raises(ValueError):
        controller.edit_domain(0, "chess.com")
    assert controller.config.domains == ["reddit.com", "chess.com"]


def test_saving_a_domain_unchanged_is_allowed(make):
    controller = make()
    controller.add_domain("reddit.com")
    controller.edit_domain(0, "reddit.com")
    assert controller.config.domains == ["reddit.com"]


def test_block_list_persists_after_restart(make):
    make().add_domain("reddit.com")
    assert make().config.domains == ["reddit.com"]
    assert config_module.load(make.path).domains == ["reddit.com"]


def test_schedule_saves_days_and_times(make):
    controller = make()
    controller.set_schedule([0, 1], "08:30", "12:00")
    assert controller.config.schedule.weekdays == [0, 1]
    assert controller.config.schedule.start == "08:30"
    assert make().config.schedule.end == "12:00"


def test_schedule_rejects_start_after_end_and_keeps_old_schedule(make):
    controller = make()
    with pytest.raises(ValueError):
        controller.set_schedule([0], "18:00", "09:00")
    assert controller.config.schedule.start == "09:00"


def test_suggestions_are_added_edited_and_removed_one_at_a_time(make):
    controller = make()
    controller.add_suggestion("  10-minute   walk ")
    controller.add_suggestion("Tidy desk")
    controller.edit_suggestion(1, "Tidy the desk")
    assert controller.config.shortlist == ["10-minute walk", "Tidy the desk"]
    controller.remove_suggestion(0)
    assert controller.config.shortlist == ["Tidy the desk"]
    state = rules.snapshot(config_module.load(make.path), MONDAY_2PM)
    assert "Tidy the desk" in render_blocked(state, "reddit.com")


def test_duplicate_or_empty_suggestion_is_refused(make):
    controller = make()
    controller.add_suggestion("10-minute walk")
    with pytest.raises(ValueError, match="already in the list"):
        controller.add_suggestion("10-Minute Walk")
    with pytest.raises(ValueError, match="Type a suggestion"):
        controller.add_suggestion("   ")
    assert controller.config.shortlist == ["10-minute walk"]


def test_history_is_empty_before_any_change(make):
    assert make().history_rows() == []


def rows(controller):
    return [(row.event, row.item, row.details) for row in controller.history_rows()]


def test_override_appears_in_history_and_status(make):
    controller = make()
    controller.add_domain("reddit.com")
    controller.override("reddit.com", "checking a work thread")
    assert rows(controller) == [
        ("Override", "reddit.com", "checking a work thread"),
        ("Site added", "reddit.com", ""),
    ]
    status = controller.status()
    assert list(status["released"]) == ["reddit.com"]
    assert status["blocked"] == []


def test_undo_reblocks_and_keeps_both_history_lines(make):
    controller = make()
    controller.add_domain("reddit.com")
    controller.override("reddit.com", "checking a work thread")
    controller.undo("reddit.com")
    assert controller.status()["blocked"] == ["reddit.com", "www.reddit.com"]
    assert controller.status()["released"] == {}
    assert rows(controller)[:2] == [
        ("Override undone", "reddit.com", ""),
        ("Override", "reddit.com", "checking a work thread"),
    ]


def test_every_change_is_recorded_newest_first(make):
    controller = make()
    controller.add_domain("chess.com")
    make.clock["now"] = datetime(2026, 10, 5, 14, 5)
    controller.edit_domain(0, "lichess.org")
    make.clock["now"] = datetime(2026, 10, 5, 14, 10)
    controller.set_schedule([0, 1, 2, 3, 4], "09:00", "17:30")
    make.clock["now"] = datetime(2026, 10, 5, 14, 15)
    controller.add_suggestion("10-minute walk")
    controller.edit_suggestion(0, "20-minute walk")
    controller.remove_suggestion(0)
    controller.remove_domain(0)
    assert rows(controller) == [
        ("Site removed", "lichess.org", ""),
        ("Suggestion removed", "20-minute walk", ""),
        ("Suggestion edited", "20-minute walk", "10-minute walk \u2192 20-minute walk"),
        ("Suggestion added", "10-minute walk", ""),
        ("Schedule changed", "", "Mon\u2013Fri, 09:00\u201317:30"),
        ("Site edited", "lichess.org", "chess.com \u2192 lichess.org"),
        ("Site added", "chess.com", ""),
    ]
    assert controller.history_rows()[0].moment == datetime(2026, 10, 5, 14, 15)


def test_unchanged_saves_are_not_recorded(make):
    controller = make()
    controller.add_domain("chess.com")
    controller.edit_domain(0, "chess.com")
    controller.set_schedule([0, 1, 2, 3, 4], "09:00", "17:00")
    controller.add_suggestion("10-minute walk")
    controller.edit_suggestion(0, "10-minute walk")
    assert rows(controller) == [("Suggestion added", "10-minute walk", ""), ("Site added", "chess.com", "")]


def test_edits_to_an_earlier_sorting_name_are_recorded(make):
    controller = make()
    controller.add_domain("lichess.org")
    controller.add_suggestion("Walk")
    controller.edit_domain(0, "chess.com")
    controller.edit_suggestion(0, "Read")
    assert rows(controller)[:2] == [
        ("Suggestion edited", "Read", "Walk \u2192 Read"),
        ("Site edited", "chess.com", "lichess.org \u2192 chess.com"),
    ]


def test_warning_text_joins_all_problems():
    assert warning_text(None) == ""
    assert warning_text(None, None, "") == ""
    assert warning_text("hosts locked", "config damaged", None) == "Warning: config damaged hosts locked"


def test_history_survives_a_restart(make):
    make().add_domain("chess.com")
    assert rows(make()) == [("Site added", "chess.com", "")]


def test_undo_without_active_override_is_rejected(make):
    controller = make()
    controller.add_domain("reddit.com")
    with pytest.raises(ValueError):
        controller.undo("reddit.com")


def test_override_is_rejected_outside_the_window(make):
    controller = make()
    controller.add_domain("reddit.com")
    make.clock["now"] = datetime(2026, 10, 5, 18, 0)
    with pytest.raises(ValueError):
        controller.override("reddit.com", "reason")


def test_countdown_advances_with_clock(make):
    controller = make()
    controller.add_domain("reddit.com")
    controller.override("reddit.com", "reason")
    make.clock["now"] = datetime(2026, 10, 5, 15, 30)
    assert controller.status()["text"] == "Window active, nothing blocked — 1h 30m remaining"


def test_window_asks_the_background_check_instead_of_writing_hosts(tmp_path):
    requests = []
    controller = Controller(
        tmp_path / "config.yaml",
        tmp_path / "hosts",
        clock=lambda: MONDAY_2PM,
        sync=lambda: requests.append("sync"),
    )
    controller.add_domain("reddit.com")
    assert requests == ["sync"]
    assert not (tmp_path / "hosts").exists()


def test_schedule_saved_from_the_window_accepts_a_single_digit_hour(make):
    controller = make()
    controller.set_schedule([0, 1, 2, 3, 4], "9:00", "17:00")
    assert controller.config.schedule.start == "09:00"


def test_schedule_without_weekdays_is_refused(make):
    controller = make()
    with pytest.raises(ValueError, match="Pick at least one day"):
        controller.set_schedule([], "09:00", "17:00")
    assert controller.config.schedule.weekdays == [0, 1, 2, 3, 4]


def test_config_with_no_weekdays_still_loads(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("domains: []\nschedule:\n  weekdays: []\n  start: '09:00'\n  end: '17:00'\n", encoding="utf-8")
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert config.schedule.weekdays == []
    assert warning is None


def test_schedule_change_stores_its_days_and_times(make):
    controller = make()
    controller.set_schedule([6, 0, 1], "8:30", "16:00")
    event = controller.config.events[-1]
    assert event["type"] == "schedule_changed"
    assert (event["weekdays"], event["start"], event["end"]) == ([6, 0, 1], "08:30", "16:00")
    assert event["details"] == "Mon, Tue, Sun, 08:30–16:00"  # still there for older Blocky versions
    assert config_module.load(make.path).events[-1] == event
