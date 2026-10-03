from datetime import datetime

import pytest

from blocky import config as config_module
from blocky.config import Config
from blocky.schedule import Schedule

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


def type_domain(app, text):
    for character in text:
        app.new_domain_entry.insert("end", character)
    app._update_domain_hint()


def test_characters_that_cannot_be_in_a_domain_are_ignored(app):
    type_domain(app, "red dit!.com")
    assert app.new_domain_entry.get() == "reddit.com"


def test_incomplete_domain_cannot_be_added(app):
    type_domain(app, "reddit")
    assert app.add_button.cget("state") == "disabled"
    assert app.domain_hint.cget("text") == "Not a full domain yet, e.g. reddit.com"
    app._add_domain()
    assert app.controller.config.domains == []


def test_valid_domain_shows_what_will_be_added(app):
    type_domain(app, "reddit.com")
    assert app.add_button.cget("state") == "normal"
    assert app.domain_hint.cget("text") == "Adds reddit.com and www.reddit.com"


def test_duplicate_domain_cannot_be_added(app):
    add(app, "reddit.com")
    type_domain(app, "reddit.com")
    assert app.add_button.cget("state") == "disabled"
    assert app.domain_hint.cget("text") == "reddit.com is already in the list"


def test_pasted_address_becomes_its_domain(app):
    app.new_domain_entry.paste_text("https://www.reddit.com/r/all?sort=new")
    assert app.new_domain_entry.get() == "www.reddit.com"
    assert app.add_button.cget("state") == "normal"


def test_override_without_reason_is_not_possible(app):
    add(app, "reddit.com")
    assert app.override_button.cget("state") == "disabled"
    assert app.override_hint.cget("text") == "Type a reason to override"
    app.reason_entry.insert(0, "   ")
    app._update_override_state()
    app._override()
    assert app.controller.status()["blocked"] == ["reddit.com", "www.reddit.com"]


def test_typing_a_reason_enables_override(app):
    add(app, "reddit.com")
    app.reason_entry.insert(0, "work thread")
    app._update_override_state()
    assert app.override_button.cget("state") == "normal"
    assert app.override_hint.cget("text") == ""


def test_override_and_undo_buttons_are_off_when_there_is_nothing_to_do(app):
    assert app.override_button.cget("state") == "disabled"
    assert app.override_hint.cget("text") == ""
    assert app.undo_button.cget("state") == "disabled"


def edit_row(app, index):
    row = app.domain_list.winfo_children()[index]
    entry, save = row.winfo_children()[0], row.winfo_children()[1]
    return entry, save


def retype(entry, text):
    entry.delete(0, "end")
    for character in text:
        entry.insert("end", character)
    entry.on_change()


def test_edit_save_is_only_possible_for_a_valid_change(app):
    add(app, "reddit.com")
    add(app, "chess.com")
    entry, save = edit_row(app, 1)
    assert save.cget("state") == "disabled"
    retype(entry, "chess")
    assert save.cget("state") == "disabled"
    retype(entry, "reddit.com")
    assert save.cget("state") == "disabled"
    retype(entry, "lichess.org")
    assert save.cget("state") == "normal"


def test_override_and_undo_update_status_and_history(app):
    add(app, "reddit.com")
    app.reason_entry.insert(0, "work thread")
    app._update_override_state()
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
    type_into(app.start_time.hour, "18")
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


def type_into(box, text):
    box.delete(0, "end")
    for character in text:
        box.insert("end", character)


def test_schedule_times_are_typed_into_guarded_fields(app):
    type_into(app.start_time.hour, "9")
    type_into(app.start_time.minute, "05")
    app._save_schedule()
    assert app.controller.config.schedule.start == "09:05"
    assert app.start_time.hour.get() == "09"
    assert app.schedule_message.cget("text") == ""


def test_invalid_typing_is_ignored(app):
    type_into(app.start_time.hour, "2a5")
    assert app.start_time.hour.get() == "2"
    type_into(app.start_time.minute, "75")
    assert app.start_time.minute.get() == "7"


def test_emptied_field_falls_back_to_the_saved_time(app):
    app.end_time.hour.delete(0, "end")
    app._save_schedule()
    assert app.controller.config.schedule.end == "17:00"


def test_saved_times_are_shown_in_the_fields(tmp_path, open_app):
    path = tmp_path / "config.yaml"
    config_module.save(path, Config(schedule=Schedule(start="09:00", end="17:58")))
    window = open_app(path, hosts_path=tmp_path / "hosts", clock=lambda: MONDAY_2PM)
    try:
        assert window.start_time.get() == "09:00"
        assert window.end_time.get() == "17:58"
    finally:
        window.destroy()
