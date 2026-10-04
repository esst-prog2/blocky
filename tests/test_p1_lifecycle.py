"""Spike p1-lifecycle, automated part: P1 cases 7 (Blocky killed) and 9 (Docker Desktop editing the hosts file).

A passing test means Blocky behaves as expected; a failing test is a gap. Results in spike/p1-lifecycle/results.md.
"""

import subprocess
import sys
import time
import tkinter
from datetime import datetime
from pathlib import Path

import pytest

from blocky import config as config_module
from blocky import hosts
from blocky.checker import Checker
from blocky.config import Config
from blocky.schedule import Schedule

ROOT = Path(__file__).resolve().parent.parent
# Docker Desktop's block, as it is in the owner's hosts file (LF line endings).
DOCKER = (
    "# Added by Docker Desktop\n"
    "10.67.73.13 host.docker.internal\n"
    "10.67.73.13 gateway.docker.internal\n"
    "# To allow the same kube context to work on the host and the container:\n"
    "127.0.0.1 kubernetes.docker.internal\n"
    "# End of section\n"
)
WINDOWS_PART = (
    "# Copyright (c) 1993-2009 Microsoft Corp.\n#\n#\t127.0.0.1       localhost\n#\t::1             localhost\n"
)


def docker_lines(text: str) -> str:
    start = text.index("# Added by Docker Desktop")
    end = text.index("# End of section") + len("# End of section\n")
    return text[start:end]


# 9a


def test_9a_docker_lines_are_unchanged_by_blocking_and_unblocking(tmp_path):
    path = tmp_path / "hosts"
    original = WINDOWS_PART + DOCKER
    path.write_bytes(original.encode("utf-8"))

    hosts.apply(["reddit.com", "www.reddit.com"], path)
    blocked = path.read_bytes().decode("utf-8")
    assert docker_lines(blocked) == DOCKER
    assert "127.0.0.1 reddit.com" in blocked

    hosts.apply([], path)
    assert path.read_bytes().decode("utf-8") == original


# 9b


def test_9b_a_docker_change_made_while_blocky_writes_survives(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    path.write_bytes((WINDOWS_PART + DOCKER).encode("utf-8"))
    moved = DOCKER.replace("10.67.73.13", "10.67.80.2")  # Docker updates its address after a network change
    real_render = hosts.render
    calls: list[str] = []

    def docker_writes_meanwhile(text, hostnames):
        # Docker Desktop writes its new address after Blocky has read the file and before Blocky writes it back.
        if not calls:
            path.write_bytes((WINDOWS_PART + moved).encode("utf-8"))
        calls.append(text)
        return real_render(text, hostnames)

    monkeypatch.setattr(hosts, "render", docker_writes_meanwhile)
    hosts.apply(["reddit.com"], path)

    written = path.read_bytes().decode("utf-8")
    assert docker_lines(written) == moved
    assert "127.0.0.1 reddit.com" in written
    assert len(calls) == 2  # read again once, after Docker's write


def test_9b_a_program_that_keeps_writing_does_not_stop_blocking(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    path.write_bytes((WINDOWS_PART + DOCKER).encode("utf-8"))
    real_render = hosts.render
    calls: list[str] = []

    def writes_every_time(text, hostnames):
        calls.append(text)
        path.write_bytes((WINDOWS_PART + DOCKER + f"# change {len(calls)}\n").encode("utf-8"))
        return real_render(text, hostnames)

    monkeypatch.setattr(hosts, "render", writes_every_time)
    hosts.apply(["reddit.com"], path)

    assert len(calls) == hosts.REREAD_ATTEMPTS  # gives up re-reading after a few tries
    assert "127.0.0.1 reddit.com" in path.read_text(encoding="utf-8")  # and still blocks


# 7a


CHECKER_SCRIPT = """
import sys, threading
from pathlib import Path
from blocky.checker import Checker
checker = Checker(Path(sys.argv[1]), Path(sys.argv[2]))
print("started", flush=True)
checker.run(threading.Event(), interval=0.2)
"""


def all_day_today() -> Schedule:
    return Schedule(weekdays=[datetime.now().weekday()], start="00:00", end="23:59")


def not_today() -> Schedule:
    return Schedule(weekdays=[(datetime.now().weekday() + 1) % 7], start="00:00", end="23:59")


def test_7a_a_new_start_after_a_kill_removes_the_entries(tmp_path):
    config_path, hosts_path = tmp_path / "config.yaml", tmp_path / "hosts"
    hosts_path.write_bytes((WINDOWS_PART + DOCKER).encode("utf-8"))
    config_module.save(config_path, Config(domains=["reddit.com"], schedule=all_day_today()))

    process = subprocess.Popen(
        [sys.executable, "-c", CHECKER_SCRIPT, str(config_path), str(hosts_path)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None and process.stdout.readline().strip() == "started"
        deadline = time.monotonic() + 15
        while "127.0.0.1 reddit.com" not in hosts_path.read_text(encoding="utf-8"):
            assert time.monotonic() < deadline, "the background check never blocked"
            time.sleep(0.1)
    finally:
        process.kill()  # like ending the task in Task Manager: no cleanup runs
        process.wait(timeout=10)

    # Killed, so the entries stay (expected, and recorded); the window then ends.
    assert "127.0.0.1 reddit.com" in hosts_path.read_text(encoding="utf-8")
    config_module.save(config_path, Config(domains=["reddit.com"], schedule=not_today()))

    Checker(config_path, hosts_path).sync()  # the first check of Blocky started again

    after = hosts_path.read_text(encoding="utf-8")
    assert hosts.BEGIN not in after
    assert after == WINDOWS_PART + DOCKER
    assert not list(tmp_path.glob("hosts.tmp"))


# 6: Windows ends the session while Blocky is open


def test_6_the_window_removes_the_blocking_when_windows_ends_the_session(tmp_path, open_app):
    calls: list[int] = []
    app = open_app(tmp_path / "config.yaml", hosts_path=tmp_path / "hosts", session_ending=lambda: calls.append(1))
    app.update()
    # What Tk runs when Windows sends WM_QUERYENDSESSION.
    app.tk.call(app.protocol("WM_SAVE_YOURSELF"))
    assert calls == [1]
    with pytest.raises(tkinter.TclError):  # the window is closed
        app.winfo_exists()


def test_6_stopping_twice_is_harmless(tmp_path):
    import threading

    from blocky.__main__ import stop_blocking

    config_path, hosts_path = tmp_path / "config.yaml", tmp_path / "hosts"
    hosts_path.write_bytes((WINDOWS_PART + DOCKER).encode("utf-8"))
    config_module.save(config_path, Config(domains=["reddit.com"], schedule=all_day_today()))
    checker = Checker(config_path, hosts_path)
    stop = threading.Event()
    worker = threading.Thread(target=checker.run, args=(stop, 60))
    worker.start()
    deadline = time.monotonic() + 15
    while "127.0.0.1 reddit.com" not in hosts_path.read_text(encoding="utf-8"):
        assert time.monotonic() < deadline
        time.sleep(0.05)

    stop_blocking(stop, worker, checker, tmp_path / "errors.log")  # when Windows ends the session
    stop_blocking(stop, worker, checker, tmp_path / "errors.log")  # and again as the window closes

    assert not worker.is_alive()
    assert hosts_path.read_text(encoding="utf-8") == WINDOWS_PART + DOCKER
    assert not (tmp_path / "errors.log").exists()


def test_6_main_gives_the_window_the_cleanup(tmp_path, monkeypatch):
    import blocky.__main__ as startup

    stopped: list[str] = []

    class FakeChecker:
        last_error = None

        def __init__(self, *args, **kwargs):
            pass

        def run(self, stop):
            stop.wait()

        def request_sync(self):
            pass

    class FakeApp:
        def __init__(self, *args, session_ending=None, **kwargs):
            self.session_ending = session_ending

        def mainloop(self):
            assert self.session_ending is not None
            self.session_ending()  # Windows ends the session while the window is open
            assert stopped == ["stopped"]

    def record_stop(stop, worker, checker, error_log):
        stop.set()
        stopped.append("stopped")

    monkeypatch.setattr(startup.dpi, "follow_each_monitor", lambda: True)
    monkeypatch.setattr(startup, "is_admin", lambda: True)
    monkeypatch.setattr(startup.ctypes.windll.shell32, "SetCurrentProcessExplicitAppUserModelID", lambda _id: 0)
    monkeypatch.setattr(startup.config_module, "default_path", lambda: tmp_path / "config.yaml")
    monkeypatch.setattr(startup, "Checker", FakeChecker)
    monkeypatch.setattr(startup, "App", FakeApp)
    monkeypatch.setattr(startup, "start_block_page", lambda _load: (None, None))
    monkeypatch.setattr(startup, "stop_blocking", record_stop)

    startup.main()

    assert stopped == ["stopped", "stopped"]  # once at the session's end, once as Blocky closes


SESSION_SCRIPT = """
import sys, threading
from pathlib import Path
from blocky.__main__ import stop_blocking
from blocky.app import App
from blocky.checker import Checker
from blocky.settings import WindowsTime

config_path, hosts_path = Path(sys.argv[1]), Path(sys.argv[2])
checker = Checker(config_path, hosts_path)
stop = threading.Event()
worker = threading.Thread(target=checker.run, args=(stop, 0.2), daemon=True)
worker.start()
app = App(
    config_path,
    hosts_path=hosts_path,
    sync=checker.request_sync,
    windows_time=lambda: WindowsTime(),
    windows_language=lambda: "en",
    session_ending=lambda: stop_blocking(stop, worker, checker, config_path.parent / "errors.log"),
)
app.update()
print(int(app.wm_frame(), 16), flush=True)
app.mainloop()
print("closed", flush=True)
"""


@pytest.mark.window
def test_6_windows_shutdown_message_removes_the_blocking_in_a_running_blocky(tmp_path):
    import ctypes

    config_path, hosts_path = tmp_path / "config.yaml", tmp_path / "hosts"
    hosts_path.write_bytes((WINDOWS_PART + DOCKER).encode("utf-8"))
    config_module.save(config_path, Config(domains=["reddit.com"], schedule=all_day_today()))
    process = subprocess.Popen(
        [sys.executable, "-c", SESSION_SCRIPT, str(config_path), str(hosts_path)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        frame = int(process.stdout.readline())
        deadline = time.monotonic() + 15
        while "127.0.0.1 reddit.com" not in hosts_path.read_text(encoding="utf-8"):
            assert time.monotonic() < deadline, "the background check never blocked"
            time.sleep(0.1)

        # What Windows sends every program's windows when it shuts down, restarts or signs out.
        ctypes.windll.user32.PostMessageW(frame, 0x0011, 0, 0)  # WM_QUERYENDSESSION

        process.wait(timeout=20)  # fails instead of hanging if the window does not close
        assert process.stdout.read().strip() == "closed"
    finally:
        process.kill()
    assert hosts_path.read_text(encoding="utf-8") == WINDOWS_PART + DOCKER
