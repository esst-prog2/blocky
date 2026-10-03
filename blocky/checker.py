import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from blocky import config as config_module
from blocky import hosts
from blocky.rules import blocked_domains


class Checker:
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path = hosts.HOSTS_PATH,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self.config_path = config_path
        self.hosts_path = hosts_path
        self.clock = clock
        self.last_error: str | None = None
        self._wake = threading.Event()

    def sync(self) -> None:
        config = config_module.load(self.config_path)
        hosts.apply(blocked_domains(config, self.clock()), self.hosts_path)

    def request_sync(self) -> None:
        self._wake.set()

    def clear(self) -> None:
        hosts.apply([], self.hosts_path)

    def run(self, stop: threading.Event, interval: float = 60) -> None:
        while not stop.is_set():
            try:
                self.sync()
                self.last_error = None
            except Exception as error:
                self.last_error = str(error)
            self._wake.wait(interval)
            self._wake.clear()
