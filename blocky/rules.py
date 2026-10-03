from datetime import datetime

from blocky.config import Config
from blocky.domains import covered_hostnames
from blocky.schedule import window_end


def released_until(config: Config, now: datetime) -> dict[str, datetime]:
    released: dict[str, datetime] = {}
    for entry in config.overrides:
        until = datetime.fromisoformat(entry["until"])
        if until > now:
            released[entry["domain"]] = until
    return released


def released_domains(config: Config, now: datetime) -> set[str]:
    return set(released_until(config, now))


def blocked_domains(config: Config, now: datetime) -> list[str]:
    if window_end(config.schedule, now) is None:
        return []
    released = released_domains(config, now)
    hostnames: list[str] = []
    for domain in config.domains:
        if domain not in released:
            hostnames.extend(covered_hostnames(domain))
    return hostnames


def overridable_domains(config: Config, now: datetime) -> list[str]:
    if window_end(config.schedule, now) is None:
        return []
    released = released_domains(config, now)
    return [domain for domain in config.domains if domain not in released]


def override(config: Config, domain: str, reason: str, now: datetime) -> None:
    reason = reason.strip()
    if not reason:
        raise ValueError("A reason is required to override a block")
    if domain not in overridable_domains(config, now):
        raise ValueError(f"{domain} is not blocked right now")
    until = window_end(config.schedule, now)
    config.overrides.append(
        {
            "domain": domain,
            "timestamp": now.isoformat(timespec="seconds"),
            "reason": reason,
            "until": until.isoformat(timespec="seconds"),
        }
    )


def status_text(config: Config, now: datetime) -> str:
    end = window_end(config.schedule, now)
    if end is None:
        return "No blocking right now"
    remaining = int((end - now).total_seconds()) // 60
    return f"Blocking active — {remaining // 60}h {remaining % 60:02d}m remaining"


def snapshot(config: Config, now: datetime) -> dict:
    end = window_end(config.schedule, now)
    return {
        "shortlist": list(config.shortlist),
        "blocked": blocked_domains(config, now),
        "windowEnd": end.strftime("%H:%M") if end else None,
    }
