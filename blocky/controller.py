from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from blocky import config as config_module
from blocky import rules
from blocky import schedule as schedule_module
from blocky.checker import Checker
from blocky.config import Config
from blocky.domains import validate
from blocky.schedule import Schedule


def warning_text(background_error: str | None, *startup_warnings: str | None) -> str:
    problems = [message for message in (*startup_warnings, background_error) if message]
    if not problems:
        return ""
    return "Warning: " + " ".join(problems)


class Controller:
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path,
        clock: Callable[[], datetime] = datetime.now,
        sync: Callable[[], None] | None = None,
    ) -> None:
        self.config_path = config_path
        self.clock = clock
        self.config: Config
        self.config, self.load_warning = config_module.load_or_recover(config_path, clock())
        self.checker = Checker(config_path, hosts_path, clock)
        # In the app, the background check is the only hosts writer and `sync` asks it to run now.
        self.sync = sync or self.checker.sync

    def save(self) -> None:
        config_module.save(self.config_path, self.config)
        self.sync()

    def add_domain(self, entry: str) -> None:
        domain = validate(entry)
        if domain in self.config.domains:
            raise ValueError(f"{domain} is already in the list")
        self.config.domains.append(domain)
        self.save()

    def edit_domain(self, index: int, entry: str) -> None:
        domain = validate(entry)
        if domain != self.config.domains[index] and domain in self.config.domains:
            raise ValueError(f"{domain} is already in the list")
        self.config.domains[index] = domain
        self.save()

    def remove_domain(self, index: int) -> None:
        del self.config.domains[index]
        self.save()

    def set_schedule(self, weekdays: list[int], start: str, end: str) -> None:
        schedule = Schedule(weekdays=weekdays, start=start, end=end)
        schedule_module.validate(schedule)
        self.config.schedule = schedule
        self.save()

    def set_shortlist(self, lines: list[str]) -> None:
        self.config.shortlist = [line.strip() for line in lines if line.strip()]
        self.save()

    def override(self, domain: str, reason: str) -> None:
        rules.override(self.config, domain, reason, self.clock())
        self.save()

    def undo(self, domain: str) -> None:
        rules.undo_override(self.config, domain, self.clock())
        self.save()

    def status(self) -> dict:
        now = self.clock()
        return {
            "text": rules.status_text(self.config, now),
            "blocked": sorted(set(rules.blocked_domains(self.config, now))),
            "released": rules.released_until(self.config, now),
            "overridable": rules.overridable_domains(self.config, now),
        }

    def history_lines(self) -> list[str]:
        return [
            f"{entry['timestamp']}  {entry['domain']}  — override undone"
            if entry.get("type") == "undo"
            else f"{entry['timestamp']}  {entry['domain']}  — {entry['reason']}"
            for entry in self.config.overrides
        ]
