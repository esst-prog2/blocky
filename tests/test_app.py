from datetime import datetime

import pytest

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)


@pytest.fixture
def app(tmp_path, open_app):
    window = open_app(tmp_path / "config.yaml", hosts_path=tmp_path / "hosts", clock=lambda: MONDAY_2PM)
    window.update()
    yield window
    window.destroy()


def add(app, domain):
    app.new_domain_entry.insert(0, domain)
    app._add_domain()
    app.update()


def test_adding_a_domain_shows_it_blocked_on_the_status_tab(app):
    add(app, "reddit.com")
    assert app.status_label.cget("text") == "Blocking active — 3h 00m remaining"
    assert app.blocked_label.cget("text") == "Blocked: reddit.com, www.reddit.com"
    assert app.override_menu.get() == "reddit.com"


def test_invalid_domain_shows_an_error_and_is_not_added(app):
    add(app, "not a domain")
    assert "not a valid domain" in app.block_message.cget("text")
    assert app.controller.config.domains == []


def test_override_without_reason_shows_an_error(app):
    add(app, "reddit.com")
    app._override()
    assert "reason is required" in app.status_message.cget("text")
    assert app.controller.status()["blocked"] == ["reddit.com", "www.reddit.com"]


def test_override_and_undo_update_status_and_history(app):
    add(app, "reddit.com")
    app.reason_entry.insert(0, "work thread")
    app._override()
    app.update()
    assert app.status_label.cget("text") == "Window active, nothing blocked — 3h 00m remaining"
    assert app.released_label.cget("text") == "reddit.com unblocked until 17:00 (3h 00m left)"
    assert app.undo_menu.get() == "reddit.com"
    assert "work thread" in app.history_box.get("1.0", "end")

    app._undo()
    app.update()
    assert app.blocked_label.cget("text") == "Blocked: reddit.com, www.reddit.com"
    assert "override undone" in app.history_box.get("1.0", "end")


def test_invalid_schedule_shows_an_error(app):
    app.start_entry.delete(0, "end")
    app.start_entry.insert(0, "18:00")
    app._save_schedule()
    assert "start time must be before the end time" in app.schedule_message.cget("text")


def test_shortlist_is_saved_without_blank_lines(app):
    app.shortlist_box.insert("1.0", "10-minute walk\n\nread notes\n")
    app._save_shortlist()
    assert app.controller.config.shortlist == ["10-minute walk", "read notes"]


def test_warning_is_shown_on_the_status_tab(tmp_path, open_app):
    window = open_app(tmp_path / "config.yaml", hosts_path=tmp_path / "hosts", warning=lambda: "Warning: test")
    window.update()
    try:
        assert window.warning_label.cget("text") == "Warning: test"
    finally:
        window.destroy()
