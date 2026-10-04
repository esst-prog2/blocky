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


def test_closing_does_not_wait_for_the_next_minute(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config(domains=["reddit.com"]))
    checker = Checker(config_path, tmp_path / "hosts", clock=lambda: datetime(2026, 10, 5, 14, 0))

    stop = threading.Event()
    worker = threading.Thread(target=checker.run, args=(stop, 60))
    worker.start()
    time.sleep(0.2)
    started = time.monotonic()
    startup.stop_blocking(stop, worker, checker, tmp_path / "errors.log")

    assert time.monotonic() - started < 2
    assert not worker.is_alive()


MONDAY_2PM = datetime(2026, 10, 5, 14, 0)


class FakeWindows:
    def __init__(self, relaunch_result=42):
        self.calls = []
        self.relaunch_result = relaunch_result
        self.windll = self
        self.shell32 = self

    def ShellExecuteW(self, *arguments):
        self.calls.append(arguments)
        return self.relaunch_result

    def SetCurrentProcessExplicitAppUserModelID(self, name):
        self.calls.append(name)


@pytest.mark.parametrize("result, accepted", [(42, True), (5, False)])
def test_relaunch_asks_for_admin_and_passes_the_arguments_on(monkeypatch, result, accepted):
    windows = FakeWindows(result)
    monkeypatch.setattr(startup, "ctypes", windows)
    monkeypatch.setattr(startup.sys, "argv", ["blocky", "--flag", "a b"])

    assert startup.relaunch_as_admin() is accepted
    _, verb, _, parameters, _, _ = windows.calls[0]
    assert verb == "runas"
    assert parameters == '-m blocky "--flag" "a b"'


class FakeServer:
    def __init__(self, load_state):
        self.load_state = load_state
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False


@pytest.fixture
def started(tmp_path, monkeypatch):
    """Runs main() as admin with a fake window, a fake block page and a hosts file in tmp_path."""
    config_path = tmp_path / "Blocky" / "config.yaml"
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    seen: dict = {"servers": []}

    def server(load_state):
        seen["servers"].append(FakeServer(load_state))
        return seen["servers"][-1]

    class Window:
        def __init__(self, path, warning, sync):
            seen["warning"] = warning

        def mainloop(self):
            deadline = time.monotonic() + 5
            while "reddit.com" not in hosts_path.read_text(encoding="utf-8") and time.monotonic() < deadline:
                time.sleep(0.05)
            seen["hosts while open"] = hosts_path.read_text(encoding="utf-8")
            # Shown if the hosts entries never appear, to tell a failed write from a sync that never ran.
            error_log = config_path.parent / "errors.log"
            seen["diagnosis"] = {
                "warning": seen["warning"](),
                "hosts.tmp left": (tmp_path / "hosts.tmp").exists(),
                "errors.log": error_log.read_text(encoding="utf-8") if error_log.exists() else None,
            }
            seen["server running"] = seen["servers"][0].running
            if seen.get("crash"):
                raise RuntimeError("window crashed")

    monkeypatch.setattr(startup, "ctypes", FakeWindows())
    monkeypatch.setattr(startup.os, "name", "nt")
    monkeypatch.setattr(startup, "is_admin", lambda: True)
    monkeypatch.setattr(startup.config_module, "default_path", lambda: config_path)
    monkeypatch.setattr(
        startup,
        "Checker",
        lambda path, error_log: Checker(path, hosts_path, clock=lambda: MONDAY_2PM, error_log=error_log),
    )
    monkeypatch.setattr(startup, "Server", server)
    monkeypatch.setattr(startup, "App", Window)
    return config_path, hosts_path, seen


def test_startup_blocks_while_open_and_cleans_up_on_close(started):
    config_path, hosts_path, seen = started
    config_module.save(config_path, Config(domains=["reddit.com"]))

    startup.main()

    assert "127.0.0.1 reddit.com" in seen["hosts while open"], seen["diagnosis"]
    assert seen["server running"]
    assert seen["warning"]() == ""
    assert hosts_path.read_text(encoding="utf-8") == "127.0.0.1 localhost\n"
    assert not seen["servers"][0].running


def test_startup_cleans_up_when_the_window_crashes(started):
    config_path, hosts_path, seen = started
    config_module.save(config_path, Config(domains=["reddit.com"]))
    seen["crash"] = True

    with pytest.raises(RuntimeError):
        startup.main()

    assert hosts_path.read_text(encoding="utf-8") == "127.0.0.1 localhost\n"
    assert not seen["servers"][0].running


def test_startup_logs_and_shows_a_damaged_config(started):
    config_path, _, seen = started
    config_path.parent.mkdir(parents=True)
    config_path.write_text("domains: [reddit.com\n", encoding="utf-8")

    startup.main()

    assert "config.yaml" in seen["warning"]()
    assert "config.yaml" in (config_path.parent / "errors.log").read_text(encoding="utf-8")
