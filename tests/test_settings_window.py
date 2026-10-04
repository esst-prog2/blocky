from datetime import datetime

import pytest

from blocky import config as config_module
from blocky import settings as settings_module
from blocky import theme as t
from blocky.app import TABS
from blocky.config import Config
from blocky.settings import FOLLOW_WINDOWS, Settings

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)
COLOUR_OPTIONS = (
    "fg_color",
    "bg_color",
    "text_color",
    "text_color_disabled",
    "hover_color",
    "border_color",
    "button_color",
    "button_hover_color",
    "dropdown_fg_color",
    "dropdown_hover_color",
    "dropdown_text_color",
    "placeholder_text_color",
    "scrollbar_button_color",
    "scrollbar_button_hover_color",
    "checkmark_color",
    "selected_color",
    "selected_hover_color",
    "unselected_color",
    "unselected_hover_color",
    "background",
    "foreground",
    "highlightbackground",
)


@pytest.fixture
def window(tmp_path, open_app):
    opened = []

    def open_window(settings=None, **kwargs):
        path = tmp_path / "config.yaml"
        if settings is not None:
            config_module.save(path, Config(domains=["reddit.com"], shortlist=["10-minute walk"], settings=settings))
        app = open_app(path, hosts_path=tmp_path / "hosts", clock=lambda: MONDAY_2PM, **kwargs)
        app.update()
        opened.append(app)
        return app

    yield open_window
    for app in opened:
        try:
            app.destroy()
        except Exception:
            pass  # the test closed it already


def colours_in(widget) -> set[str]:
    """Every colour the widget and its children use, except theme previews, which show other themes on purpose."""
    if getattr(widget, "preview", False):
        return set()
    found = set()
    for option in COLOUR_OPTIONS:
        try:
            value = widget.cget(option)
        except Exception:
            continue
        for colour in value if isinstance(value, tuple | list) else [value]:
            if isinstance(colour, str) and colour.startswith("#"):
                found.add(colour.upper())
    for child in widget.winfo_children():
        found |= colours_in(child)
    return found


def choose(app, **changes):
    app._choose(**changes)
    app.update()


@pytest.mark.parametrize("name", [name for name in settings_module.THEMES if name != "forest"])
def test_switching_theme_leaves_no_forest_colour(window, name):
    app = window()
    app.tabs.set("Settings")
    forest = colours_in(app)
    assert forest & {value.upper() for value in t.THEMES["forest"].values()}

    choose(app, theme=name)

    leftovers = {value.upper() for value in t.THEMES["forest"].values()} - {
        value.upper() for value in t.THEMES[name].values()
    }
    assert colours_in(app) & leftovers == set()
    assert {value.upper() for value in t.THEMES[name].values()} & colours_in(app)
    assert app.tabs.get() == "Settings"
    assert app.cget("fg_color") == t.THEMES[name]["BACKGROUND"]
    assert app.icon_path.name == f"blocky-{name}.ico"
    assert app.icon_path.exists()


def test_every_theme_has_its_icon_file():
    from blocky.app import ASSETS

    for name in settings_module.THEMES:
        assert (ASSETS / f"blocky-{name}.ico").read_bytes()[:4] == b"\x00\x00\x01\x00"
    assert (ASSETS / "blocky.ico").exists()  # the shortcut keeps the Forest icon


def test_redraw_keeps_the_open_tab(window):
    app = window()
    for tab in TABS:
        app.tabs.set(tab)
        app.redraw()
        assert app.tabs.get() == tab


def test_theme_choice_is_saved_and_kept_after_reopening(window, tmp_path):
    app = window()
    app.tabs.set("Settings")
    app.theme_tiles["navy"].choose()
    app.update()
    assert t.THEME == "navy"
    assert config_module.load(tmp_path / "config.yaml").settings.theme == "navy"
    app.destroy()
    t.apply()

    again = window()
    assert again.controller.config.settings.theme == "navy"
    assert again.cget("fg_color") == t.THEMES["navy"]["BACKGROUND"]
    assert "✓ Navy" in [child.cget("text") for child in again.theme_tiles["navy"].winfo_children()[:1]]


def test_clicking_a_theme_tile_chooses_it(window):
    app = window()
    title = next(child for child in app.theme_tiles["aqua"].winfo_children() if hasattr(child, "_label"))
    app.tabs.set("Settings")
    app.update()
    title._label.event_generate("<Button-1>", x=4, y=4)
    app.update()
    assert app.controller.config.settings.theme == "aqua"


def test_font_buttons_each_show_their_own_font(window):
    app = window()
    for name, button in app.font_buttons.items():
        assert button.cget("font").cget("family") == t.font_spec("body", name)[0]


def test_font_choice_changes_the_window_and_is_kept(window, tmp_path):
    app = window()
    app.font_buttons["Georgia"].invoke()
    app.update()
    assert app.status_label.cget("font").cget("family") == "Georgia"
    assert app.list_title.cget("font").cget("family") == "Georgia"
    assert config_module.load(tmp_path / "config.yaml").settings.font == "Georgia"
    app.destroy()
    t.apply()
    assert window().status_label.cget("font").cget("family") == "Georgia"


def test_text_size_changes_the_window_and_is_kept(window, tmp_path):
    app = window()
    app.size_buttons["extra-large"].invoke()
    app.update()
    assert app.status_label.cget("font").cget("size") == round(24 * 1.3)
    assert app.add_button.cget("height") == round(36 * 1.3)
    assert config_module.load(tmp_path / "config.yaml").settings.text_size == "extra-large"
    assert app.tabs.get() == "Status"


def test_choosing_the_current_value_does_not_redraw(window):
    app = window()
    label = app.status_label
    choose(app, theme="forest")
    assert label.winfo_exists()


# Reset


def test_reset_restores_defaults_and_keeps_the_data(window, tmp_path):
    app = window(Settings(theme="blossom", font="Georgia", text_size="large"))
    app.tabs.set("Settings")
    app.reset_button.invoke()
    app.update()
    assert app.controller.config.settings == Settings()
    assert t.THEME == "forest"
    saved = config_module.load(tmp_path / "config.yaml")
    assert saved.settings == Settings()
    assert saved.domains == ["reddit.com"]
    assert saved.shortlist == ["10-minute walk"]
    assert app.reset_notice.winfo_manager() == "pack"  # survives the redraw
    assert app.tabs.get() == "Settings"


def test_undo_brings_back_and_saves_the_earlier_settings(window, tmp_path):
    chosen = Settings(theme="blossom", font="Georgia", text_size="large")
    app = window(chosen)
    app.reset_button.invoke()
    app.update()
    app.undo_reset_button.invoke()
    app.update()
    assert app.controller.config.settings == chosen
    assert config_module.load(tmp_path / "config.yaml").settings == chosen
    assert t.THEME == "blossom"
    assert app.reset_notice.winfo_manager() == ""


def test_reset_message_goes_away_with_the_next_change(window):
    app = window(Settings(theme="blossom"))
    app.reset_button.invoke()
    app.update()
    choose(app, theme="sand")
    assert app.reset_notice.winfo_manager() == ""
    assert app.settings_before_reset is None


# Follow Windows


def test_follow_windows_switches_with_the_windows_mode(window):
    mode = {"light": True}
    reads = []

    def windows_is_light():
        reads.append(1)
        return mode["light"]

    app = window(
        Settings(theme=FOLLOW_WINDOWS, dark_theme="navy", light_theme="blossom"), windows_is_light=windows_is_light
    )
    assert t.THEME == "blossom"
    assert set(app.follow_choices) == {"dark_theme", "light_theme"}

    label = app.status_label
    app._poll_windows_mode()
    assert label.winfo_exists()  # same mode: no redraw

    mode["light"] = False
    app._poll_windows_mode()
    assert t.THEME == "navy"
    assert not label.winfo_exists()


def test_windows_mode_is_not_read_without_follow_windows(window):
    reads = []

    def windows_is_light():
        reads.append(1)
        return True

    app = window(windows_is_light=windows_is_light)
    app._poll_windows_mode()
    assert reads == []
    assert t.THEME == "forest"


def test_dark_and_light_choices_under_follow_windows(window):
    app = window(Settings(theme=FOLLOW_WINDOWS), windows_is_light=lambda: False)
    assert t.THEME == "forest"
    app.follow_choices["dark_theme"]["navy"].invoke()
    app.update()
    assert t.THEME == "navy"
    assert app.controller.config.settings.dark_theme == "navy"


def test_the_poll_runs_every_two_seconds(window):
    from blocky.app import WINDOWS_MODE_POLL_MS

    app = window()
    assert WINDOWS_MODE_POLL_MS == 2000
    assert app._poll_id in app.tk.call("after", "info")


# Extra large


@pytest.mark.parametrize("name", settings_module.THEMES)
def test_every_tab_opens_at_extra_large(window, name):
    app = window(Settings(theme=name, text_size="extra-large"))
    for tab in TABS:
        app.tabs.set(tab)
        app.update()
    assert name == t.THEME


def test_settings_scroll_to_the_last_row_at_the_smallest_size(window):
    app = window(Settings(theme=FOLLOW_WINDOWS, text_size="extra-large"), windows_is_light=lambda: False)
    app.tabs.set("Settings")
    app.geometry(f"{app._min_width}x{app._min_height}")
    app.update()
    canvas = app.settings_scroll._parent_canvas
    canvas.yview_moveto(1.0)
    app.update()
    top = canvas.winfo_rooty()
    bottom = top + canvas.winfo_height()
    button = app.reset_button
    assert top <= button.winfo_rooty()
    assert button.winfo_rooty() + button.winfo_height() <= bottom
