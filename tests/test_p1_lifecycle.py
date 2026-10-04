"""Spike p1-lifecycle, automated part: P1 cases 7 (Blocky killed) and 9 (Docker Desktop editing the hosts file).

A passing test means Blocky behaves as expected; a failing test is a gap. Results in spike/p1-lifecycle/results.md.
"""

import subprocess
import sys
import time
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


@pytest.mark.xfail(strict=True, reason="gap: Blocky writes back the hosts file as it read it (spike p1-lifecycle)")
def test_9b_a_docker_change_made_while_blocky_writes_survives(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    path.write_bytes((WINDOWS_PART + DOCKER).encode("utf-8"))
    moved = DOCKER.replace("10.67.73.13", "10.67.80.2")  # Docker updates its address after a network change
    real_write = hosts.write_safely

    def docker_writes_first(target, data):
        # Docker Desktop writes its new address after Blocky has read the file and before Blocky writes it back.
        target.write_bytes((WINDOWS_PART + moved).encode("utf-8"))
        real_write(target, data)

    monkeypatch.setattr(hosts, "write_safely", docker_writes_first)
    hosts.apply(["reddit.com"], path)

    assert docker_lines(path.read_bytes().decode("utf-8")) == moved


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
