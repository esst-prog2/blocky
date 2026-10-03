import threading
from datetime import datetime
from pathlib import Path

import pytest

from blocky import config as config_module
from blocky import hosts
from blocky.checker import Checker
from blocky.config import Config
from blocky.controller import Controller
from blocky.schedule import Schedule, window_end

NOON = datetime(2026, 10, 5, 14, 0)


def test_checker_keeps_running_after_unexpected_error(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker = Checker(config_path, tmp_path / "hosts", clock=lambda: NOON)
    stop = threading.Event()
    calls = {"count": 0}

    def sync_that_fails_once():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("unexpected")
        stop.set()

    checker.sync = sync_that_fails_once
    try:
        checker.run(stop, interval=0)
    except RuntimeError:
        pytest.fail("checker stopped after an unexpected error, so blocking would stop silently")
    assert calls["count"] == 2


def test_hosts_reset_by_another_program_is_restored_by_next_sync(tmp_path):
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker = Checker(config_path, hosts_path, clock=lambda: NOON)
    checker.sync()
    assert "127.0.0.1 reddit.com" in hosts_path.read_text(encoding="utf-8")

    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    checker.sync()
    assert "127.0.0.1 reddit.com" in hosts_path.read_text(encoding="utf-8")


def test_failed_hosts_write_leaves_original_file_intact(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    original = "127.0.0.1 localhost\n" * 50
    path.write_text(original, encoding="utf-8")

    def write_half_then_fail(self, data):
        with open(self, "wb") as handle:
            handle.write(data[: len(data) // 2])
        raise OSError("disk error during write")

    monkeypatch.setattr(Path, "write_bytes", write_half_then_fail)
    with pytest.raises(OSError):
        hosts.apply(["reddit.com"], path)
    assert path.read_text(encoding="utf-8") == original


def test_window_logic_across_daylight_saving_end():
    schedule = Schedule(weekdays=[0, 1, 2, 3, 4, 5, 6], start="01:00", end="03:30")
    before_change = datetime(2026, 10, 25, 1, 30)
    repeated_hour = datetime(2026, 10, 25, 2, 30)
    after_change = datetime(2026, 10, 25, 3, 15)
    assert window_end(schedule, before_change) is not None
    assert window_end(schedule, repeated_hour) is not None
    assert window_end(schedule, after_change) is not None


def test_override_survives_restart(tmp_path):
    clock = {"now": NOON}
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    first = Controller(config_path, hosts_path, clock=lambda: clock["now"])
    first.add_domain("reddit.com")
    first.override("reddit.com", "checking a work thread")

    reopened = Controller(config_path, hosts_path, clock=lambda: clock["now"])
    assert "reddit.com" in reopened.status()["released"]

    clock["now"] = datetime(2026, 10, 5, 17, 0)
    assert reopened.status()["released"] == {}


def test_removed_domain_leaves_hosts_file_mid_window(tmp_path):
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    controller = Controller(config_path, hosts_path, clock=lambda: NOON)
    controller.add_domain("reddit.com")
    assert "reddit.com" in hosts_path.read_text(encoding="utf-8")

    controller.remove_domain(0)
    assert "reddit.com" not in hosts_path.read_text(encoding="utf-8")
