import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from blocky.schedule import Schedule


@dataclass
class Config:
    domains: list[str] = field(default_factory=list)
    schedule: Schedule = field(default_factory=Schedule)
    shortlist: list[str] = field(default_factory=list)
    overrides: list[dict] = field(default_factory=list)


def default_path() -> Path:
    return Path(os.environ.get("APPDATA", Path.home())) / "Blocky" / "config.yaml"


def load(path: Path) -> Config:
    if not path.exists():
        return Config()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    schedule = data.get("schedule", {})
    return Config(
        domains=list(data.get("domains", [])),
        schedule=Schedule(
            weekdays=list(schedule.get("weekdays", [0, 1, 2, 3, 4])),
            start=schedule.get("start", "09:00"),
            end=schedule.get("end", "17:00"),
        ),
        shortlist=list(data.get("shortlist", [])),
        overrides=list(data.get("overrides", [])),
    )


def save(path: Path, config: Config) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        yaml.safe_dump(asdict(config), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    temporary.replace(path)
