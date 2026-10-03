from datetime import datetime

import pytest

from blocky.config import Config
from blocky.rules import blocked_domains, override, released_until, snapshot, status_text


def at(day, hour, minute=0):
    return datetime(2026, 10, day, hour, minute)


def make_config(**kwargs):
    return Config(domains=["reddit.com"], **kwargs)


def test_blocked_inside_window_includes_www_variant():
    assert blocked_domains(make_config(), at(5, 14)) == ["reddit.com", "www.reddit.com"]


def test_nothing_blocked_outside_window():
    assert blocked_domains(make_config(), at(5, 18)) == []


def test_override_requires_reason():
    with pytest.raises(ValueError):
        override(make_config(), "reddit.com", "   ", at(5, 14))


def test_override_requires_currently_blocked_domain():
    with pytest.raises(ValueError):
        override(make_config(), "reddit.com", "reason", at(5, 18))


def test_override_unblocks_until_window_end():
    config = make_config()
    override(config, "reddit.com", "checking a work thread", at(5, 14))
    assert blocked_domains(config, at(5, 15)) == []
    assert config.overrides[0]["until"] == "2026-10-05T17:00:00"


def test_released_until_gives_window_end_for_overridden_domain():
    config = make_config()
    override(config, "reddit.com", "reason", at(5, 14))
    assert released_until(config, at(5, 14, 30)) == {"reddit.com": at(5, 17)}


def test_override_expires_and_blocks_again_next_window():
    config = make_config()
    override(config, "reddit.com", "reason", at(5, 14))
    assert blocked_domains(config, at(5, 17)) == []
    assert blocked_domains(config, at(6, 9)) == ["reddit.com", "www.reddit.com"]


def test_override_is_logged_with_domain_timestamp_and_reason():
    config = make_config()
    override(config, "reddit.com", "checking a work thread", at(5, 14))
    entry = config.overrides[0]
    assert entry["domain"] == "reddit.com"
    assert entry["timestamp"] == "2026-10-05T14:00:00"
    assert entry["reason"] == "checking a work thread"


def test_status_text_shows_remaining_time():
    assert status_text(make_config(), at(5, 14)) == "Blocking active — 3h 00m remaining"


def test_snapshot_reports_blocked_hostnames_and_window_end():
    config = make_config(shortlist=["10-minute walk"])
    assert snapshot(config, at(5, 14)) == {
        "shortlist": ["10-minute walk"],
        "blocked": ["reddit.com", "www.reddit.com"],
        "windowEnd": "17:00",
    }
