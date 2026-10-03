from blocky.config import Config, load, save
from blocky.schedule import Schedule


def test_missing_file_loads_defaults(tmp_path):
    config = load(tmp_path / "config.yaml")
    assert config.domains == []
    assert config.schedule == Schedule()
    assert config.shortlist == []
    assert config.overrides == []


def test_saved_config_round_trips(tmp_path):
    path = tmp_path / "nested" / "config.yaml"
    original = Config(
        domains=["reddit.com", "youtube.com"],
        schedule=Schedule(weekdays=[0, 2], start="08:30", end="12:00"),
        shortlist=["read lecture notes", "10-minute walk"],
        overrides=[
            {
                "domain": "reddit.com",
                "timestamp": "2026-10-05T14:00:00",
                "reason": "checking a work thread",
                "until": "2026-10-05T17:00:00",
            }
        ],
    )
    save(path, original)
    assert load(path) == original
