import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from blocky import config as config_module
from blocky import hosts
from blocky.rules import blocked_domains


def log_error(error_log: Path | None, message: str) -> None:
    if error_log is None:
        return
    try:
        error_log.parent.mkdir(parents=True, exist_ok=True)
        with error_log.open("a", encoding="utf-8") as log:
            log.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n")
    except OSError:
        pass


class Checker:
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path = hosts.HOSTS_PATH,
        clock: Callable[[], datetime] = datetime.now,
        error_log: Path | None = None,
    ) -> None:
        self.config_path = config_path
        self.hosts_path = hosts_path
        self.clock = clock
        self.error_log = error_log
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
                if str(error) != self.last_error:
                    log_error(self.error_log, f"Background check failed: {error!r}")
                self.last_error = str(error)
            self._wake.wait(interval)
            self._wake.clear()
