from datetime import datetime
from pathlib import Path

import pytest

from blocky import config as config_module
from blocky.checker import Checker
from blocky.config import Config

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)

DAMAGED = {
    "invalid YAML": "domains: [reddit.com\n",
    "zero bytes": "\x00" * 64,
    "empty file": "",
    "domains as text": "domains: reddit.com\n",
}


def test_config_save_succeeds_when_the_swap_is_briefly_locked(tmp_path, monkeypatch):
    path = tmp_path / "config.yaml"
    real_replace = Path.replace
    failures = {"left": 3}

    def locked_replace(self, target):
        if failures["left"]:
            failures["left"] -= 1
            raise PermissionError(13, "Access is denied")
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", locked_replace)
    config_module.save(path, Config(domains=["reddit.com"]))
    assert config_module.load(path).domains == ["reddit.com"]


@pytest.mark.parametrize("text", DAMAGED.values(), ids=DAMAGED.keys())
def test_damaged_config_opens_the_window_with_a_warning(tmp_path, open_app, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    window = open_app(path, hosts_path=tmp_path / "hosts", clock=lambda: MONDAY_2PM)
    try:
        window.update()
        assert "config.yaml" in window.warning_label.cget("text")
    finally:
        window.destroy()
    assert path.read_text(encoding="utf-8") == text


@pytest.mark.parametrize("text", DAMAGED.values(), ids=DAMAGED.keys())
def test_damaged_config_writes_no_wrong_hosts_entries(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    checker = Checker(path, hosts_path, clock=lambda: MONDAY_2PM)
    try:
        checker.sync()
    except Exception:
        pass
    assert "127.0.0.1 r\n" not in hosts_path.read_text(encoding="utf-8")
