from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from blocky import config as config_module
from blocky import history, rules
from blocky import schedule as schedule_module
from blocky import suggestions as suggestions_module
from blocky.checker import Checker
from blocky.clock import DEFAULT_STYLE, TimeStyle
from blocky.config import Config
from blocky.domains import validate
from blocky.language import _
from blocky.schedule import Schedule
from blocky.settings import Settings


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
            raise ValueError(_("{domain} is already in the list", domain=domain))
        self.config.domains.append(domain)
        self._record("site_added", domain)
        self.save()

    def edit_domain(self, index: int, entry: str) -> None:
        domain = validate(entry)
        if domain != self.config.domains[index] and domain in self.config.domains:
            raise ValueError(_("{domain} is already in the list", domain=domain))
        old = self.config.domains[index]
        self.config.domains[index] = domain
        if domain != old:
            self._record("site_edited", domain, f"{old} → {domain}")
        self.save()

    def remove_domain(self, index: int) -> None:
        removed = self.config.domains.pop(index)
        self._record("site_removed", removed)
        self.save()

    def set_schedule(self, weekdays: list[int], start: str, end: str) -> None:
        if not weekdays:
            raise ValueError(_("Pick at least one day"))
        schedule = Schedule(
            weekdays=weekdays,
            start=schedule_module.parse_time(start),
            end=schedule_module.parse_time(end),
        )
        schedule_module.validate(schedule)
        if schedule != self.config.schedule:
            details = history.describe_schedule(schedule.weekdays, schedule.start, schedule.end)
            # The days and times themselves too, so History can show them in whatever format is chosen later.
            fields = {"weekdays": list(schedule.weekdays), "start": schedule.start, "end": schedule.end}
            self._record("schedule_changed", "", details, **fields)
        self.config.schedule = schedule
        self.save()

    def add_suggestion(self, text: str) -> None:
        suggestion = suggestions_module.check(text, self.config.shortlist)
        self.config.shortlist.append(suggestion)
        self._record("suggestion_added", suggestion)
        self.save()

    def edit_suggestion(self, index: int, text: str) -> None:
        old = self.config.shortlist[index]
        suggestion = suggestions_module.check(text, self.config.shortlist, original=old)
        self.config.shortlist[index] = suggestion
        if suggestion != old:
            self._record("suggestion_edited", suggestion, f"{old} → {suggestion}")
        self.save()

    def remove_suggestion(self, index: int) -> None:
        removed = self.config.shortlist.pop(index)
        self._record("suggestion_removed", removed)
        self.save()

    def set_settings(self, settings: Settings) -> None:
        self.config.settings = settings
        config_module.save(self.config_path, self.config)  # nothing to block or unblock, so no hosts sync

    def reset_settings(self) -> Settings:
        """Put every setting back to its default and return the settings from before, for Undo."""
        before = self.config.settings
        self.set_settings(Settings())
        return before

    def _record(self, kind: str, item: str, details: str = "", **fields: object) -> None:
        timestamp = self.clock().isoformat(timespec="seconds")
        self.config.events.append({"type": kind, "timestamp": timestamp, "item": item, "details": details, **fields})

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

    def history_rows(self, style: TimeStyle = DEFAULT_STYLE) -> list[history.Row]:
        return history.rows(self.config.events, self.config.overrides, style)
