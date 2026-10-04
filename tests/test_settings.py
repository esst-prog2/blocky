import dataclasses
from datetime import datetime

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from blocky import config as config_module
from blocky import settings as settings_module
from blocky.config import Config
from blocky.controller import Controller
from blocky.schedule import Schedule
from blocky.settings import FOLLOW_WINDOWS, Settings, effective_theme

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)


def test_defaults_are_todays_look_and_forest_and_sand_for_follow_windows():
    assert Settings() == Settings(
        theme="forest", dark_theme="forest", light_theme="sand", font="Segoe UI Variable", text_size="normal"
    )


def test_the_offered_choices():
    assert settings_module.DARK_THEMES == ("forest", "navy")
    assert settings_module.LIGHT_THEMES == ("sand", "aqua", "blossom")
    assert len(settings_module.FONTS) == 10
    assert settings_module.TEXT_SIZES == {"small": 0.9, "normal": 1.0, "large": 1.15, "extra-large": 1.3}


def test_labels():
    assert [settings_module.label(size) for size in settings_module.TEXT_SIZES] == [
        "Small",
        "Normal",
        "Large",
        "Extra large",
    ]
    assert settings_module.label("follow-windows") == "Follow windows"


@pytest.mark.parametrize("light", [False, True])
@pytest.mark.parametrize("chosen", settings_module.THEMES)
def test_a_chosen_theme_ignores_windows(chosen, light):
    assert effective_theme(Settings(theme=chosen, dark_theme="navy", light_theme="aqua"), light) == chosen


@pytest.mark.parametrize("light_theme", settings_module.LIGHT_THEMES)
@pytest.mark.parametrize("dark_theme", settings_module.DARK_THEMES)
def test_follow_windows_uses_the_dark_or_light_choice(dark_theme, light_theme):
    chosen = Settings(theme=FOLLOW_WINDOWS, dark_theme=dark_theme, light_theme=light_theme)
    assert effective_theme(chosen, windows_is_light=False) == dark_theme
    assert effective_theme(chosen, windows_is_light=True) == light_theme


def test_follow_windows_without_choices_uses_forest_and_sand():
    assert effective_theme(Settings(theme=FOLLOW_WINDOWS), False) == "forest"
    assert effective_theme(Settings(theme=FOLLOW_WINDOWS), True) == "sand"


# Loading


def load_text(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return config_module.load_or_recover(path, MONDAY_2PM)


def test_missing_section_gives_the_defaults(tmp_path):
    config, warning = load_text(tmp_path, "domains:\n- reddit.com\n")
    assert config.settings == Settings()
    assert warning is None


@pytest.mark.parametrize("section", ["settings: purple\n", "settings: [1, 2]\n", "settings:\n", "settings: 3\n"])
def test_a_section_that_is_not_a_mapping_gives_the_defaults(tmp_path, section):
    config, warning = load_text(tmp_path, "domains:\n- reddit.com\n" + section)
    assert config.settings == Settings()
    assert config.domains == ["reddit.com"]
    assert warning is None


def test_unknown_theme_falls_back_on_its_own(tmp_path):
    config, warning = load_text(tmp_path, "domains:\n- reddit.com\nsettings:\n  theme: Purple\n  font: Calibri\n")
    assert config.settings == Settings(font="Calibri")
    assert config.domains == ["reddit.com"]
    assert warning is None
    assert not list(tmp_path.glob("*.damaged-*"))


@pytest.mark.parametrize(
    "field, bad",
    [
        ("theme", "Navy"),
        ("theme", 3),
        ("dark_theme", "sand"),  # a light theme cannot be the dark choice
        ("light_theme", "navy"),
        ("font", "Comic Sans MS"),
        ("font", ["Calibri"]),
        ("text_size", 1.15),
        ("text_size", None),
    ],
)
def test_each_wrong_value_falls_back_without_touching_the_others(tmp_path, field, bad):
    chosen = Settings(theme="aqua", dark_theme="navy", light_theme="blossom", font="Georgia", text_size="large")
    data = {**settings_module.to_data(chosen), field: bad}
    config, warning = load_text(tmp_path, yaml.safe_dump({"settings": data}))
    assert config.settings == Settings(**{**settings_module.to_data(chosen), field: getattr(Settings(), field)})
    assert warning is None


def test_each_missing_field_falls_back_on_its_own(tmp_path):
    config, _ = load_text(tmp_path, "settings:\n  text_size: extra-large\n")
    assert config.settings == Settings(text_size="extra-large")


def test_settings_round_trip(tmp_path):
    path = tmp_path / "config.yaml"
    chosen = Settings(
        theme=FOLLOW_WINDOWS, dark_theme="navy", light_theme="aqua", font="Bahnschrift", text_size="small"
    )
    config_module.save(path, Config(domains=["reddit.com"], settings=chosen))
    assert config_module.load(path) == Config(domains=["reddit.com"], settings=chosen)
    assert "settings:" in path.read_text(encoding="utf-8")


yaml_values = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(),
    lambda children: st.lists(children) | st.dictionaries(st.text(), children),
    max_leaves=10,
)


@given(st.one_of(yaml_values, st.dictionaries(st.sampled_from(list(settings_module.CHOICES)), yaml_values)))
@settings(deadline=None)
def test_any_yaml_value_in_the_section_loads(section):
    text = yaml.safe_dump({"domains": ["reddit.com"], "settings": section})
    config, warnings = config_module._parse(text)
    assert config.domains == ["reddit.com"]
    assert warnings == []
    for key, choices in settings_module.CHOICES.items():
        assert getattr(config.settings, key) in choices


# A config.yaml as Blocky wrote it before settings existed.
TODAYS_FORMAT = """\
domains:
- reddit.com
- youtube.com
schedule:
  weekdays:
  - 0
  - 2
  - 4
  start: 08:30
  end: '16:00'
shortlist:
- 10-minute walk
- read lecture notes
overrides:
- type: override
  domain: reddit.com
  timestamp: '2026-10-05T14:00:00'
  reason: work thread
  until: '2026-10-05T16:00:00'
- type: undo
  domain: reddit.com
  timestamp: '2026-10-05T14:30:00'
events:
- type: site_added
  timestamp: '2026-10-05T13:00:00'
  item: reddit.com
  details: ''
- type: schedule_changed
  timestamp: '2026-10-05T13:05:00'
  item: ''
  details: Mon, Wed, Fri 08:30–16:00
"""
TODAYS_CONFIG = Config(
    domains=["reddit.com", "youtube.com"],
    schedule=Schedule(weekdays=[0, 2, 4], start="08:30", end="16:00"),
    shortlist=["10-minute walk", "read lecture notes"],
    overrides=[
        {
            "type": "override",
            "domain": "reddit.com",
            "timestamp": "2026-10-05T14:00:00",
            "reason": "work thread",
            "until": "2026-10-05T16:00:00",
        },
        {"type": "undo", "domain": "reddit.com", "timestamp": "2026-10-05T14:30:00"},
    ],
    events=[
        {"type": "site_added", "timestamp": "2026-10-05T13:00:00", "item": "reddit.com", "details": ""},
        {
            "type": "schedule_changed",
            "timestamp": "2026-10-05T13:05:00",
            "item": "",
            "details": "Mon, Wed, Fri 08:30–16:00",
        },
    ],
)


def test_a_config_in_todays_format_loads_and_saves_unchanged(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(TODAYS_FORMAT, encoding="utf-8")
    config, warning = config_module.load_or_recover(path, MONDAY_2PM)
    assert warning is None
    assert config == TODAYS_CONFIG
    assert config.settings == Settings()
    assert not list(tmp_path.glob("*.damaged-*"))

    config_module.save(path, config)
    assert config_module.load(path) == TODAYS_CONFIG
    saved = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert {key: value for key, value in saved.items() if key != "settings"} == yaml.safe_load(TODAYS_FORMAT)


# Controller


@pytest.fixture
def controller(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(TODAYS_FORMAT, encoding="utf-8")
    return Controller(path, tmp_path / "hosts", clock=lambda: MONDAY_2PM)


def test_set_settings_is_saved(controller):
    chosen = Settings(theme="blossom", font="Georgia", text_size="large")
    controller.set_settings(chosen)
    assert controller.config.settings == chosen
    assert config_module.load(controller.config_path).settings == chosen


def test_reset_changes_only_the_settings(controller):
    chosen = Settings(theme="blossom", font="Georgia", text_size="large")
    controller.set_settings(chosen)
    assert controller.reset_settings() == chosen
    assert controller.config == TODAYS_CONFIG
    assert config_module.load(controller.config_path) == TODAYS_CONFIG


def test_changing_settings_writes_no_history(controller):
    controller.set_settings(Settings(theme="navy"))
    controller.reset_settings()
    assert controller.config.events == TODAYS_CONFIG.events


def test_unreadable_windows_mode_means_dark(monkeypatch):
    import winreg

    def fail(*_args):
        raise OSError("no such value")

    monkeypatch.setattr(winreg, "OpenKey", fail)
    assert settings_module.windows_is_light() is False


@pytest.mark.parametrize("value, light", [(1, True), (0, False)])
def test_windows_mode_is_read_from_the_registry(monkeypatch, value, light):
    import contextlib
    import winreg

    monkeypatch.setattr(winreg, "OpenKey", lambda *_args: contextlib.nullcontext())
    monkeypatch.setattr(winreg, "QueryValueEx", lambda _key, name: (value if name == "AppsUseLightTheme" else 9, 4))
    assert settings_module.windows_is_light() is light


def test_block_page_state_carries_the_effective_appearance(tmp_path, monkeypatch):
    from blocky.__main__ import page_state

    path = tmp_path / "config.yaml"
    chosen = Settings(theme=FOLLOW_WINDOWS, dark_theme="navy", light_theme="aqua", font="Georgia", text_size="large")
    config_module.save(path, Config(domains=["reddit.com"], settings=chosen))
    monkeypatch.setattr(settings_module, "windows_is_light", lambda: True)
    assert page_state(path)["appearance"] == {"theme": "aqua", "font": "Georgia", "text_size": "large"}
    monkeypatch.setattr(settings_module, "windows_is_light", lambda: False)
    assert page_state(path)["appearance"]["theme"] == "navy"
    assert page_state(path)["shortlist"] == []


def test_settings_cannot_change_in_place():
    # Undo keeps the earlier Settings object; it must stay as it was.
    import dataclasses

    with pytest.raises(dataclasses.FrozenInstanceError):
        Settings().theme = "navy"  # type: ignore[misc]


# Time format and first day of the week


def test_time_settings_follow_windows_by_default():
    assert Settings().time_format == FOLLOW_WINDOWS
    assert Settings().first_day == FOLLOW_WINDOWS


def test_part_one_config_loads_with_both_time_settings_at_follow_windows(tmp_path):
    config, warning = load_text(tmp_path, "settings:\n  theme: navy\n  font: Calibri\n  text_size: large\n")
    assert config.settings == Settings(theme="navy", font="Calibri", text_size="large")
    assert (config.settings.time_format, config.settings.first_day) == (FOLLOW_WINDOWS, FOLLOW_WINDOWS)
    assert warning is None


@pytest.mark.parametrize(
    "field, bad", [("time_format", "12"), ("time_format", True), ("first_day", "wednesday"), ("first_day", 6)]
)
def test_wrong_time_settings_fall_back_on_their_own(tmp_path, field, bad):
    chosen = Settings(theme="aqua", time_format="12h", first_day="sunday")
    config, warning = load_text(tmp_path, yaml.safe_dump({"settings": {**settings_module.to_data(chosen), field: bad}}))
    assert config.settings == dataclasses.replace(chosen, **{field: FOLLOW_WINDOWS})
    assert warning is None


WINDOWS_12 = settings_module.WindowsTime(twelve_hour=True, first_day=6)
WINDOWS_24 = settings_module.WindowsTime(twelve_hour=False, first_day=0)


@pytest.mark.parametrize("windows", [WINDOWS_12, WINDOWS_24, settings_module.WindowsTime(first_day=2)])
@pytest.mark.parametrize("time_format", [FOLLOW_WINDOWS, "24h", "12h"])
@pytest.mark.parametrize("first_day", [FOLLOW_WINDOWS, "monday", "saturday", "sunday"])
def test_time_style_for_every_combination(windows, time_format, first_day):
    style = settings_module.time_style(Settings(time_format=time_format, first_day=first_day), windows)
    assert style.twelve_hour == (windows.twelve_hour if time_format == FOLLOW_WINDOWS else time_format == "12h")
    expected_day = {"monday": 0, "saturday": 5, "sunday": 6}.get(first_day, windows.first_day)
    assert style.first_day == expected_day


def fake_international(monkeypatch, values):
    import contextlib
    import winreg

    def query(_key, name):
        if name not in values:
            raise FileNotFoundError(name)
        return values[name], winreg.REG_SZ

    monkeypatch.setattr(winreg, "OpenKey", lambda *_args: contextlib.nullcontext())
    monkeypatch.setattr(winreg, "QueryValueEx", query)


@pytest.mark.parametrize(
    "short_time, twelve_hour", [("HH:mm", False), ("H:mm", False), ("h:mm tt", True), ("hh:mm tt", True), ("", False)]
)
def test_windows_time_format_is_read_from_the_short_time(monkeypatch, short_time, twelve_hour):
    fake_international(monkeypatch, {"sShortTime": short_time, "iFirstDayOfWeek": "0"})
    assert settings_module.windows_time().twelve_hour is twelve_hour


@pytest.mark.parametrize(
    "value, first_day", [*[(str(day), day) for day in range(7)], ("7", 0), ("x", 0), ("", 0), ("²", 0)]
)
def test_windows_first_day_is_read_from_the_registry(monkeypatch, value, first_day):
    fake_international(monkeypatch, {"sShortTime": "HH:mm", "iFirstDayOfWeek": value})
    assert settings_module.windows_time().first_day == first_day


def test_unreadable_windows_time_means_24_hour_and_monday(monkeypatch):
    fake_international(monkeypatch, {})
    assert settings_module.windows_time() == settings_module.WindowsTime(twelve_hour=False, first_day=0)

    import winreg

    def fail(*_args):
        raise OSError("no such key")

    monkeypatch.setattr(winreg, "OpenKey", fail)
    assert settings_module.windows_time() == settings_module.WindowsTime(twelve_hour=False, first_day=0)


def test_windows_values_of_the_wrong_type_are_ignored(monkeypatch):
    fake_international(monkeypatch, {"sShortTime": 12, "iFirstDayOfWeek": 6})
    assert settings_module.windows_time() == settings_module.WindowsTime(twelve_hour=False, first_day=0)
