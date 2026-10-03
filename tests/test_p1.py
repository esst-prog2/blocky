import threading
import time
from datetime import datetime

import pytest

import blocky.__main__ as startup
from blocky import config as config_module
from blocky.__main__ import start_block_page
from blocky.checker import Checker
from blocky.config import Config
from blocky.controller import Controller, warning_text


def test_clock_jump_forward_unblocks_after_window_end(tmp_path):
    clock = {"now": datetime(2026, 10, 5, 16, 59)}
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker = Checker(config_path, hosts_path, clock=lambda: clock["now"])

    checker.sync()
    assert "reddit.com" in hosts_path.read_text(encoding="utf-8")

    clock["now"] = datetime(2026, 10, 5, 17, 1)
    checker.sync()
    assert "reddit.com" not in hosts_path.read_text(encoding="utf-8")


def test_clock_jump_backwards_reblocks(tmp_path):
    clock = {"now": datetime(2026, 10, 5, 17, 1)}
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker = Checker(config_path, hosts_path, clock=lambda: clock["now"])

    checker.sync()
    assert "reddit.com" not in hosts_path.read_text(encoding="utf-8")

    clock["now"] = datetime(2026, 10, 5, 16, 30)
    checker.sync()
    assert "reddit.com" in hosts_path.read_text(encoding="utf-8")


def test_port_in_use_still_lets_blocking_run(monkeypatch):
    def server_that_cannot_bind(load_state):
        raise OSError("port 8765 is in use")

    monkeypatch.setattr(startup, "Server", server_that_cannot_bind)
    server, warning = start_block_page(dict)
    assert server is None
    assert warning is not None


def test_background_hosts_failure_is_shown_to_user(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config(domains=["reddit.com"]))
    hosts_as_folder = tmp_path / "hosts"
    hosts_as_folder.mkdir()
    controller = Controller(config_path, hosts_as_folder, clock=lambda: datetime(2026, 10, 5, 14, 0))

    stop = threading.Event()
    worker = threading.Thread(target=controller.checker.run, args=(stop, 0))
    worker.start()
    time.sleep(0.3)
    stop.set()
    worker.join()

    assert controller.checker.last_error is not None
    assert warning_text(controller.checker.last_error, None) != ""


def test_closing_blocky_removes_its_entries(tmp_path):
    config_path = tmp_path / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker = Checker(config_path, hosts_path, clock=lambda: datetime(2026, 10, 5, 14, 0))

    stop = threading.Event()
    worker = threading.Thread(target=checker.run, args=(stop, 0.05))
    worker.start()
    time.sleep(0.2)
    assert "reddit.com" in hosts_path.read_text(encoding="utf-8")

    startup.stop_blocking(stop, worker, checker, tmp_path / "errors.log")
    time.sleep(0.2)

    text = hosts_path.read_text(encoding="utf-8")
    assert "reddit.com" not in text
    assert "127.0.0.1 localhost" in text


def test_closing_blocky_survives_a_hosts_failure(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config(domains=["reddit.com"]))
    hosts_as_folder = tmp_path / "hosts"
    hosts_as_folder.mkdir()
    checker = Checker(config_path, hosts_as_folder)

    stop = threading.Event()
    worker = threading.Thread(target=checker.run, args=(stop, 0))
    worker.start()
    startup.stop_blocking(stop, worker, checker, tmp_path / "errors.log")

    assert not worker.is_alive()
    assert "Could not remove" in (tmp_path / "errors.log").read_text(encoding="utf-8")


@pytest.mark.parametrize("accepted, shown", [(False, 1), (True, 0)])
def test_declined_uac_prompt_shows_a_message(monkeypatch, accepted, shown):
    messages = []
    monkeypatch.setattr(startup.os, "name", "nt")
    monkeypatch.setattr(startup, "is_admin", lambda: False)
    monkeypatch.setattr(startup, "relaunch_as_admin", lambda: accepted)
    monkeypatch.setattr(startup, "show_admin_needed", lambda: messages.append(startup.ADMIN_NEEDED))

    startup.main()

    assert len(messages) == shown
