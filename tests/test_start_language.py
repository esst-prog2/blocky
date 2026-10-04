"""What Blocky shows before its window opens is in the stored language, or Windows' under Follow Windows."""

import ctypes

import pytest

import blocky.__main__ as startup
from blocky import config as config_module
from blocky import language
from blocky.config import Config
from blocky.settings import FOLLOW_WINDOWS, Settings


def save_language(tmp_path, code):
    path = tmp_path / "config.yaml"
    config_module.save(path, Config(settings=Settings(language=code)))
    return path


@pytest.mark.parametrize(
    ("stored", "windows", "expected"),
    [("nl", "hu", "nl"), (FOLLOW_WINDOWS, "hu", "hu"), (FOLLOW_WINDOWS, "other", "en"), ("en", "nl", "en")],
)
def test_start_language_is_the_stored_or_windows_language(tmp_path, monkeypatch, stored, windows, expected):
    monkeypatch.setattr(language, "windows_language", lambda: windows)
    assert startup.start_language(save_language(tmp_path, stored)) == expected


@pytest.mark.parametrize("text", [None, "domains: [reddit.com\n", "domains: reddit.com\n"])
def test_missing_or_damaged_config_follows_windows(tmp_path, monkeypatch, text):
    path = tmp_path / "config.yaml"
    if text is not None:
        path.write_text(text, encoding="utf-8")
    monkeypatch.setattr(language, "windows_language", lambda: "hu")
    assert startup.start_language(path) == "hu"
    if text is not None:
        assert path.read_text(encoding="utf-8") == text  # recovering is left to main()


def test_administrator_message_in_dutch(tmp_path, monkeypatch):
    shown = []
    monkeypatch.setattr(ctypes.windll.user32, "MessageBoxW", lambda _owner, text, title, _flags: shown.append(text))
    monkeypatch.setattr(startup.config_module, "default_path", lambda: save_language(tmp_path, "nl"))
    monkeypatch.setattr(startup.os, "name", "nt")
    monkeypatch.setattr(startup, "is_admin", lambda: False)
    monkeypatch.setattr(startup, "relaunch_as_admin", lambda: False)
    monkeypatch.setattr(startup.dpi, "follow_each_monitor", lambda: True)

    startup.main()

    assert shown == [
        "Blocky heeft beheerdersrechten nodig om het hosts-bestand aan te passen. Start Blocky opnieuw en kies Ja."
    ]


def test_damaged_config_warning_in_dutch_with_english_in_the_log(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("domains: [reddit.com\n", encoding="utf-8")
    log = tmp_path / "errors.log"
    language.apply("nl")

    warning = startup.recover_config(path, log)

    assert warning is not None
    assert warning.startswith("config.yaml kon niet worden gelezen (het is geen geldige YAML), dus Blocky")
    logged = log.read_text(encoding="utf-8")
    assert "config.yaml could not be read (it is not valid YAML), so Blocky started with an empty list." in logged
    assert "kon niet" not in logged


def test_block_page_warning_in_hungarian(monkeypatch):
    def refuse(*_args, **_kwargs):
        raise OSError("port in use")

    monkeypatch.setattr(startup, "Server", refuse)
    language.apply("hu")
    server, warning = startup.start_block_page(dict)
    assert server is None
    assert warning == (
        "A tiltóoldal nem tudott elindulni, ezért a tiltott webhelyeken a böngésző hibaoldala jelenik meg: port in use"
    )


class Once:
    """A stop event that lets the check loop run exactly once."""

    def __init__(self):
        self.asked = 0

    def is_set(self):
        self.asked += 1
        return self.asked > 1


def test_hosts_error_is_shown_translated_and_logged_in_english(tmp_path):
    from blocky.checker import Checker

    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("# BEGIN BLOCKY\n# BEGIN BLOCKY\n", encoding="utf-8")
    config_path = tmp_path / "config.yaml"
    config_module.save(config_path, Config())
    log = tmp_path / "errors.log"
    checker = Checker(config_path, hosts_path, error_log=log)
    language.apply("nl")

    checker.run(Once(), interval=0)  # type: ignore[arg-type]

    assert checker.last_error == "Geneste Blocky-sectie in het hosts-bestand"
    assert "ValueError('Nested Blocky section in the hosts file')" in log.read_text(encoding="utf-8")
