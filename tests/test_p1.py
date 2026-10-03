import socket
import threading
import time
from datetime import datetime

import pytest

from blocky import config as config_module
from blocky.checker import Checker
from blocky.config import Config
from blocky.controller import Controller
from blocky.server import Server


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


def test_port_in_use_still_lets_blocking_run(tmp_path):
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    port = blocker.getsockname()[1]
    try:
        with pytest.raises(OSError):
            Server(lambda: {}, port=port)
        pytest.fail(
            "the block page server cannot start when port 8765 is taken, and main() "
            "stops before the checker can keep running; blocking would stop with it"
        )
    finally:
        blocker.close()


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
    assert controller.status().get("warning"), "the user is not shown that blocking failed"
