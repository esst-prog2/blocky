from datetime import datetime

import pytest

from blocky import config as config_module
from blocky import rules
from blocky.app import App
from blocky.server import render_home

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)


@pytest.fixture
def make_app(tmp_path):
    apps = []
    clock = {"now": MONDAY_2PM}

    def factory():
        try:
            app = App(tmp_path / "config.yaml", hosts_path=tmp_path / "hosts", clock=lambda: clock["now"])
        except Exception as error:
            pytest.skip(f"no display available: {error}")
        app.checker.clock = app.clock
        app.update()
        apps.append(app)
        return app

    factory.clock = clock
    factory.path = tmp_path / "config.yaml"
    yield factory
    for app in apps:
        app.destroy()


def add_domain(app, entry):
    app.new_domain_entry.delete(0, "end")
    app.new_domain_entry.insert(0, entry)
    app._add_domain()


def test_block_list_add_edit_remove(make_app):
    app = make_app()
    add_domain(app, "reddit.com")
    assert app.config.domains == ["reddit.com"]
    app._edit_domain(0, "youtube.com")
    assert app.config.domains == ["youtube.com"]
    app._remove_domain(0)
    assert app.config.domains == []


def test_invalid_domain_is_rejected_with_message(make_app):
    app = make_app()
    add_domain(app, "reddit")
    assert app.config.domains == []
    assert app.block_message.cget("text") != ""


def test_block_list_persists_after_restart(make_app):
    app = make_app()
    add_domain(app, "reddit.com")
    reopened = make_app()
    assert reopened.config.domains == ["reddit.com"]
    assert config_module.load(make_app.path).domains == ["reddit.com"]


def test_schedule_saves_selected_days_and_times(make_app):
    app = make_app()
    for index, box in enumerate(app.day_boxes):
        box.select() if index < 2 else box.deselect()
    app.start_entry.delete(0, "end")
    app.start_entry.insert(0, "08:30")
    app._save_schedule()
    assert app.config.schedule.weekdays == [0, 1]
    assert app.config.schedule.start == "08:30"


def test_schedule_rejects_start_after_end(make_app):
    app = make_app()
    app.start_entry.delete(0, "end")
    app.start_entry.insert(0, "18:00")
    app._save_schedule()
    assert app.config.schedule.start == "09:00"
    assert app.schedule_message.cget("text") != ""


def test_shortlist_edits_appear_on_next_page_load(make_app):
    app = make_app()
    app.shortlist_box.insert("1.0", "10-minute walk\n\nread lecture notes\n")
    app._save_shortlist()
    assert app.config.shortlist == ["10-minute walk", "read lecture notes"]
    state = rules.snapshot(config_module.load(make_app.path), MONDAY_2PM)
    assert "read lecture notes" in render_home(state)


def test_history_is_empty_then_lists_override(make_app):
    app = make_app()
    assert app.history_box.get("1.0", "end").strip() == "No overrides yet."
    add_domain(app, "reddit.com")
    app._refresh_status()
    app.reason_entry.insert(0, "checking a work thread")
    app._override()
    history = app.history_box.get("1.0", "end")
    assert "reddit.com" in history
    assert "checking a work thread" in history


def test_status_shows_unblocked_until_and_countdown(make_app):
    app = make_app()
    add_domain(app, "reddit.com")
    app.reason_entry.insert(0, "reason")
    app._override()
    assert "reddit.com unblocked until 17:00" in app.released_label.cget("text")
    assert "(3h 00m left)" in app.released_label.cget("text")


def test_countdown_advances_with_clock(make_app):
    app = make_app()
    add_domain(app, "reddit.com")
    app.reason_entry.insert(0, "reason")
    app._override()
    make_app.clock["now"] = datetime(2026, 10, 5, 15, 30)
    app._refresh_status()
    assert "(1h 30m left)" in app.released_label.cget("text")
