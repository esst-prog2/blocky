from datetime import datetime

import pytest

from blocky import config as config_module
from blocky import rules
from blocky.controller import Controller
from blocky.server import render_home

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

    factory.clock = clock
    factory.path = tmp_path / "config.yaml"
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


def test_shortlist_edits_appear_on_next_page_load(make):
    controller = make()
    controller.set_shortlist(["10-minute walk", "", "read lecture notes  "])
    assert controller.config.shortlist == ["10-minute walk", "read lecture notes"]
    state = rules.snapshot(config_module.load(make.path), MONDAY_2PM)
    assert "read lecture notes" in render_home(state)


def test_history_is_empty_before_any_override(make):
    assert make().history_lines() == []


def test_override_appears_in_history_and_status(make):
    controller = make()
    controller.add_domain("reddit.com")
    controller.override("reddit.com", "checking a work thread")
    assert controller.history_lines() == [
        "2026-10-05T14:00:00  reddit.com  — checking a work thread"
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
    assert controller.history_lines() == [
        "2026-10-05T14:00:00  reddit.com  — checking a work thread",
        "2026-10-05T14:00:00  reddit.com  — override undone",
    ]


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
