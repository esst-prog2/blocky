import threading
import time
from datetime import datetime

from blocky import config as config_module
from blocky.checker import Checker, log_error
from blocky.config import Config
from blocky.hosts import BEGIN


def test_sync_adds_entries_inside_window(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config(domains=["reddit.com"]))
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")

    checker = Checker(config_path, hosts_path, clock=lambda: datetime(2026, 10, 5, 14, 0))
    checker.sync()

    text = hosts_path.read_text(encoding="utf-8")
    assert "127.0.0.1 reddit.com" in text
    assert "127.0.0.1 www.reddit.com" in text


def test_sync_removes_leftover_entries_outside_window(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config(domains=["reddit.com"]))
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text(f"{BEGIN}\n127.0.0.1 reddit.com\n# END BLOCKY\n", encoding="utf-8")

    checker = Checker(config_path, hosts_path, clock=lambda: datetime(2026, 10, 5, 18, 0))
    checker.sync()

    assert BEGIN not in hosts_path.read_text(encoding="utf-8")


def test_sync_request_wakes_the_checker_before_the_interval(tmp_path):
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    config_module.save(config_path, Config(domains=[]))
    checker = Checker(config_path, hosts_path, clock=lambda: datetime(2026, 10, 5, 14, 0))

    stop = threading.Event()
    worker = threading.Thread(target=checker.run, args=(stop, 60))
    worker.start()
    time.sleep(0.2)
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker.request_sync()
    deadline = time.monotonic() + 5
    while "reddit.com" not in hosts_path.read_text(encoding="utf-8") and time.monotonic() < deadline:
        time.sleep(0.05)
    text = hosts_path.read_text(encoding="utf-8")

    stop.set()
    checker.request_sync()
    worker.join(timeout=2)
    assert "127.0.0.1 reddit.com" in text
    assert not worker.is_alive()


def test_an_unwritable_error_log_does_not_stop_the_checker(tmp_path):
    blocker = tmp_path / "not-a-folder"
    blocker.write_text("", encoding="utf-8")
    log_error(blocker / "errors.log", "Background check failed")
    assert blocker.read_text(encoding="utf-8") == ""
