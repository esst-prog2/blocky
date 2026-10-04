import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

from blocky import domains as domains_module
from blocky import schedule as schedule_module
from blocky import settings as settings_module
from blocky.files import write_safely
from blocky.schedule import Schedule
from blocky.settings import Settings


class DamagedConfig(ValueError):
    pass


@dataclass
class Config:
    domains: list[str] = field(default_factory=list)
    schedule: Schedule = field(default_factory=Schedule)
    shortlist: list[str] = field(default_factory=list)
    overrides: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)


def default_path() -> Path:
    return Path(os.environ.get("APPDATA", Path.home())) / "Blocky" / "config.yaml"


def _list(data: dict, key: str, default: list) -> list:
    value = data.get(key, default)
    if not isinstance(value, list):
        raise DamagedConfig(f"'{key}' is not a list")
    return value


def _check_override(entry: object) -> None:
    if not isinstance(entry, dict) or not isinstance(entry.get("domain"), str):
        raise DamagedConfig("an override entry has no domain")
    if entry.get("type") != "undo":
        try:
            datetime.fromisoformat(entry["until"])
        except (KeyError, TypeError, ValueError):
            raise DamagedConfig("an override entry has no valid end time") from None


def _check_event(entry: object) -> None:
    if not isinstance(entry, dict) or not isinstance(entry.get("type"), str):
        raise DamagedConfig("a history entry has no type")
    try:
        datetime.fromisoformat(entry["timestamp"])
    except (KeyError, TypeError, ValueError):
        raise DamagedConfig("a history entry has no valid time") from None


def _parse(text: str) -> tuple[Config, list[str]]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        raise DamagedConfig("it is not valid YAML") from None
    if not isinstance(data, dict):
        raise DamagedConfig("it is empty or not a Blocky config")

    schedule_data = data.get("schedule", {})
    if not isinstance(schedule_data, dict):
        raise DamagedConfig("'schedule' is not a section")
    schedule = Schedule(
        weekdays=_list(schedule_data, "weekdays", [0, 1, 2, 3, 4]),
        start=str(schedule_data.get("start", "09:00")),
        end=str(schedule_data.get("end", "17:00")),
    )
    try:
        schedule_module.validate(schedule)
    except (TypeError, ValueError):
        raise DamagedConfig("the schedule is not valid") from None

    skipped: list[str] = []
    domains: list[str] = []
    for entry in _list(data, "domains", []):
        try:
            domains.append(domains_module.validate(str(entry)))
        except ValueError:
            skipped.append(str(entry))
    overrides = _list(data, "overrides", [])
    for entry in overrides:
        _check_override(entry)
    shortlist = [str(item) for item in _list(data, "shortlist", [])]
    events = _list(data, "events", [])
    for entry in events:
        _check_event(entry)

    # Settings never count as damage: each unknown value falls back to its default on its own.
    settings = settings_module.from_data(data.get("settings"))

    warnings = [f"Skipped invalid domains in the config: {', '.join(skipped)}."] if skipped else []
    config = Config(
        domains=domains, schedule=schedule, shortlist=shortlist, overrides=overrides, events=events, settings=settings
    )
    return config, warnings


def load(path: Path) -> Config:
    if not path.exists():
        return Config()
    return _parse(path.read_bytes().decode("utf-8", errors="replace"))[0]


def load_or_recover(path: Path, now: datetime) -> tuple[Config, str | None]:
    """Load the config; if it is damaged, keep a copy under a new name and start empty."""
    if not path.exists():
        return Config(), None
    try:
        config, warnings = _parse(path.read_bytes().decode("utf-8", errors="replace"))
    except DamagedConfig as problem:
        copy = path.with_name(f"{path.name}.damaged-{now:%Y%m%d-%H%M%S}")
        path.replace(copy)
        return Config(), (
            f"{path.name} could not be read ({problem}), so Blocky started with an empty list. "
            f"The old file was kept as {copy.name}."
        )
    return config, " ".join(warnings) or None


def save(path: Path, config: Config) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Escaping non-ASCII keeps every character intact; PyYAML would read an unescaped U+0085 back as a space.
    text = yaml.safe_dump(asdict(config), sort_keys=False, allow_unicode=False)
    write_safely(path, text.encode("utf-8"))
