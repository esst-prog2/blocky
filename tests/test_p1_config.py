from datetime import datetime

import pytest

from blocky import config as config_module
from blocky import files
from blocky.checker import Checker
from blocky.config import Config

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)

DAMAGED = {
    "invalid YAML": "domains: [reddit.com\n",
    "zero bytes": "\x00" * 64,
    "empty file": "",
    "domains as text": "domains: reddit.com\n",
}

DAMAGED_PARTS = {
    "schedule as text": ("schedule: weekdays\n", "'schedule' is not a section"),
    "start after end": ("schedule:\n  start: '18:00'\n  end: '09:00'\n", "schedule is not valid"),
    "override without domain": ("overrides:\n- until: '2026-10-05T15:00:00'\n", "override entry has no domain"),
    "override without end time": ("overrides:\n- domain: reddit.com\n  until: soon\n", "no valid end time"),
    "history entry without type": ("events:\n- timestamp: '2026-10-05T14:00:00'\n", "history entry has no type"),
}


def test_config_save_succeeds_when_the_swap_is_briefly_locked(tmp_path, monkeypatch):
    path = tmp_path / "config.yaml"
    real_replace = files.os.replace
    failures = {"left": 3}

    def locked_replace(source, target):
        if failures["left"]:
            failures["left"] -= 1
            raise PermissionError(13, "Access is denied")
        return real_replace(source, target)

    monkeypatch.setattr(files.os, "replace", locked_replace)
    monkeypatch.setattr(files, "REPLACE_DELAY", 0)
    config_module.save(path, Config(domains=["reddit.com"]))
    assert config_module.load(path).domains == ["reddit.com"]


@pytest.mark.parametrize("text", DAMAGED.values(), ids=DAMAGED.keys())
def test_damaged_config_opens_the_window_with_a_warning(tmp_path, open_app, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    window = open_app(path, hosts_path=tmp_path / "hosts", clock=lambda: MONDAY_2PM)
    try:
        window.update()
        assert "config.yaml" in window.warning_label.cget("text")
    finally:
        window.destroy()
    copies = list(tmp_path.glob("config.yaml.damaged-*"))
    assert len(copies) == 1
    assert copies[0].read_text(encoding="utf-8") == text


@pytest.mark.parametrize("text", DAMAGED.values(), ids=DAMAGED.keys())
def test_damaged_config_writes_no_wrong_hosts_entries(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    checker = Checker(path, hosts_path, clock=lambda: MONDAY_2PM)
    try:
        checker.sync()
    except Exception:
        pass
    assert "127.0.0.1 r\n" not in hosts_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("text, reason", DAMAGED_PARTS.values(), ids=DAMAGED_PARTS.keys())
def test_damaged_part_of_a_config_is_named_in_the_warning(tmp_path, text, reason):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert config == Config()
    assert reason in warning
    assert len(list(tmp_path.glob("config.yaml.damaged-*"))) == 1


def test_config_lives_in_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert config_module.default_path() == tmp_path / "Blocky" / "config.yaml"


def test_invalid_domains_in_a_good_config_are_skipped_with_a_warning(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("domains:\n- reddit.com\n- not a domain\n", encoding="utf-8")
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert config.domains == ["reddit.com"]
    assert "not a domain" in warning
    assert path.exists()


def test_a_good_config_loads_without_a_warning(tmp_path):
    path = tmp_path / "config.yaml"
    config_module.save(path, Config(domains=["reddit.com"], shortlist=["walk"]))
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert config.domains == ["reddit.com"]
    assert warning is None


def test_config_without_events_loads_with_an_empty_history(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("domains:\n- reddit.com\n", encoding="utf-8")
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert config.events == []
    assert warning is None


def test_config_with_a_broken_history_entry_counts_as_damaged(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("domains: []\nevents:\n- type: site_added\n  timestamp: yesterday\n", encoding="utf-8")
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert "history entry" in warning
