import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

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

    def sync(self) -> None:
        config = config_module.load(self.config_path)
        hosts.apply(blocked_domains(config, self.clock()), self.hosts_path)

    def run(self, stop: threading.Event, interval: float = 60) -> None:
        while not stop.is_set():
            try:
                self.sync()
                self.last_error = None
            except (OSError, ValueError) as error:
                self.last_error = str(error)
            stop.wait(interval)
