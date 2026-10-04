import pytest

from blocky import settings as settings_module
from blocky import theme

# Every (text, surface) pair the window shows, and the WCAG 2.1 ratio it needs.
TEXT_PAIRS = [
    *[(text, surface) for text in ("TEXT", "MUTED", "ACCENT") for surface in ("BACKGROUND", "CARD", "HOVER")],
    ("WARNING", "CARD"),  # warning banner and hints
    ("DANGER", "CARD"),  # error messages
    ("DANGER", "HOVER"),  # Remove under the pointer
    ("ON_DEEP", "DEEP"),  # status heading, selected tab, highlighted menu entry
    ("ON_DEEP", "CARD"),  # tab and menu text on the unselected ones
    ("ON_DEEP", "HOVER"),
    ("SOFT_ON_DEEP", "DEEP"),
    ("ON_PRIMARY", "PRIMARY"),
    ("ON_PRIMARY", "PRIMARY_HOVER"),
]
PAIRS = [(text, surface, 4.5) for text, surface in TEXT_PAIRS] + [
    ("BORDER", "BACKGROUND", 3.0),
    ("BORDER", "CARD", 3.0),
    ("DISABLED_TEXT", "DISABLED", 3.0),  # disabled main button
    ("DISABLED_TEXT", "CARD", 3.0),  # disabled text button
]

# Pairs in the approved colours that fall short, all on HOVER (shaded History rows and buttons under the pointer).
# Accepted by the owner on 2026-10-04, since fixing them would change Forest or the approved values. This list may only
# shrink: a new pair below the minimum fails the test.
KNOWN_GAPS = {
    ("forest", "ACCENT", "HOVER"),
    ("forest", "DANGER", "HOVER"),
    ("navy", "MUTED", "HOVER"),
    ("navy", "ACCENT", "HOVER"),
    ("navy", "DANGER", "HOVER"),
    ("sand", "DANGER", "HOVER"),
}


def luminance(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    red, green, blue = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def too_pale(themes: dict[str, dict[str, str]]) -> set[tuple[str, str, str]]:
    return {
        (name, text, surface)
        for name, colours in themes.items()
        for text, surface, minimum in PAIRS
        if contrast(colours[text], colours[surface]) < minimum
    }


def test_contrast_is_computed_as_wcag_defines_it():
    assert contrast("#000000", "#FFFFFF") == pytest.approx(21)
    assert contrast("#777777", "#FFFFFF") == pytest.approx(4.48, abs=0.01)


def test_every_theme_has_every_role_as_a_colour():
    assert set(theme.THEMES) == set(settings_module.THEMES)
    for colours in theme.THEMES.values():
        assert set(colours) == set(theme.ROLES)
        assert all(len(value) == 7 and value.startswith("#") for value in colours.values())


def test_every_text_colour_is_readable_on_its_surfaces():
    assert too_pale(theme.THEMES) <= KNOWN_GAPS


def test_known_gaps_are_still_gaps():
    # When one is fixed, take it off the list so it cannot come back unnoticed.
    assert too_pale(theme.THEMES) == KNOWN_GAPS


def test_a_too_pale_colour_is_caught():
    themes = {name: dict(colours) for name, colours in theme.THEMES.items()}
    themes["aqua"]["MUTED"] = "#7FC4C7"
    assert ("aqua", "MUTED", "CARD") in too_pale(themes)


def test_widgets_made_after_apply_use_the_new_theme(tk_root):
    theme.apply("navy")
    navy = theme.THEMES["navy"]
    assert theme.label(tk_root, "x").cget("text_color") == navy["TEXT"]
    assert theme.card(tk_root).cget("fg_color") == navy["CARD"]
    assert theme.quiet_button(tk_root, "x", None).cget("text_color") == navy["ACCENT"]
    chip = theme.chip(tk_root, "x")
    assert (chip.cget("fg_color"), chip.cget("text_color")) == (navy["BACKGROUND"], navy["TEXT"])
    assert theme.Message(tk_root).cget("text_color") == navy["MUTED"]
    assert theme.primary_button(tk_root, "x", None).cget("fg_color") == navy["PRIMARY"]
    assert theme.entry_style()["border_color"] == navy["BORDER"]


def test_explicit_colours_still_win(tk_root):
    theme.apply("aqua")
    assert theme.label(tk_root, "x", color=theme.WARNING).cget("text_color") == "#6B4500"
    assert theme.Message(tk_root, theme.DANGER).cget("text_color") == "#A63A2B"


def test_apply_sets_every_role():
    for name, colours in theme.THEMES.items():
        theme.apply(name)
        assert name == theme.THEME
        assert {role: getattr(theme, role) for role in theme.ROLES} == colours


@pytest.mark.parametrize("name", settings_module.THEMES)
def test_light_themes_switch_customtkinter_to_light_mode(name):
    import customtkinter as ctk

    theme.apply(name)
    expected = "light" if name in settings_module.LIGHT_THEMES else "dark"
    assert ctk.get_appearance_mode().lower() == expected


@pytest.mark.parametrize("size, scale", settings_module.TEXT_SIZES.items())
@pytest.mark.parametrize("font_name", settings_module.FONTS)
def test_font_roles_follow_the_font_and_size(font_name, size, scale):
    theme.apply("forest", font_name, size)
    for role, base in theme.SIZES.items():
        family, points, weight = theme.font_spec(role)
        assert points == round(base * scale)
        if font_name == "Segoe UI Variable":
            assert (family, weight) == theme.VARIABLE_ROLES[role]
        else:
            assert family == font_name
            assert weight == ("bold" if role in ("display", "brand", "title", "button") else "normal")


def test_font_can_be_asked_for_another_font_than_the_current_one():
    theme.apply("forest", "Calibri", "large")
    assert theme.font_spec("body", "Georgia") == ("Georgia", 15, "normal")


@pytest.mark.parametrize(
    "size, control, chip, width",
    [("small", 32, 23, 94), ("normal", 36, 26, 104), ("large", 41, 30, 120), ("extra-large", 47, 34, 135)],
)
def test_fixed_sizes_scale_with_the_text_size(size, control, chip, width):
    theme.apply("forest", "Segoe UI Variable", size)
    assert (theme.CONTROL_HEIGHT, theme.CHIP_HEIGHT, theme.px(104)) == (control, chip, width)


# Today's look, copied from theme.py before themes existed; Forest and the defaults must keep it.
FOREST_BEFORE = {
    "BACKGROUND": "#273338",
    "CARD": "#2F3E44",
    "HOVER": "#35474D",
    "BORDER": "#7D928A",
    "TEXT": "#F1F4EC",
    "MUTED": "#A9B5AD",
    "DEEP": "#2B5748",
    "ON_DEEP": "#F1F4EC",
    "SOFT_ON_DEEP": "#C6D3C2",
    "ACCENT": "#9CB080",
    "PRIMARY": "#9CB080",
    "PRIMARY_HOVER": "#B4C4A2",
    "ON_PRIMARY": "#273338",
    "DISABLED": "#3A4A4F",
    "DISABLED_TEXT": "#8A9690",
    "WARNING": "#E8B85C",
    "DANGER": "#EE8F7F",
}
FONTS_BEFORE = {
    "display": ("Segoe UI Variable Display", 24, "bold"),
    "title": ("Segoe UI Variable Text Semibold", 15, "normal"),
    "body": ("Segoe UI Variable Text", 13, "normal"),
    "caption": ("Segoe UI Variable Text", 12, "normal"),
    "button": ("Segoe UI Variable Text Semibold", 13, "normal"),
    "brand": ("Segoe UI Variable Display", 20, "bold"),
}


def test_default_look_is_todays_look():
    defaults = settings_module.Settings()
    theme.apply(defaults.theme, defaults.font, defaults.text_size)
    assert theme.THEMES["forest"] == FOREST_BEFORE
    assert {role: getattr(theme, role) for role in theme.ROLES} == FOREST_BEFORE
    assert {role: theme.font_spec(role) for role in theme.SIZES} == FONTS_BEFORE
    assert (theme.CONTROL_HEIGHT, theme.CHIP_HEIGHT) == (36, 26)


def test_forest_is_the_look_before_any_apply():
    import importlib

    importlib.reload(theme)
    assert {role: getattr(theme, role) for role in theme.ROLES} == FOREST_BEFORE


def test_set_enabled_shows_the_state_on_main_buttons_only(tk_root):
    theme.apply("sand")
    main = theme.primary_button(tk_root, "Add", None)
    quiet = theme.quiet_button(tk_root, "Save", None)
    theme.set_enabled(main, False)
    theme.set_enabled(quiet, False)
    assert (main.cget("fg_color"), main.cget("state")) == (theme.DISABLED, "disabled")
    assert (quiet.cget("fg_color"), quiet.cget("state")) == ("transparent", "disabled")
    theme.set_enabled(main, True)
    theme.set_enabled(quiet, True)
    assert (main.cget("fg_color"), main.cget("state")) == (theme.PRIMARY, "normal")
    assert (quiet.cget("fg_color"), quiet.cget("state")) == ("transparent", "normal")


def test_message_takes_space_only_while_it_has_text(tk_root):
    message = theme.Message(tk_root)
    message.configure(text="Type a reason")
    assert message.winfo_manager() == ""  # not placed until packed
    message.pack(fill="x")
    assert message.winfo_manager() == "pack"
    message.configure(text="")
    assert message.winfo_manager() == ""
    message.configure(text="Type a reason")
    assert message.winfo_manager() == "pack"
    message.configure(text_color=theme.DANGER)
    assert message.winfo_manager() == "pack"
    message.configure(text="")
    assert message.winfo_manager() == ""


@pytest.mark.parametrize(
    "hex_color, value",
    [("#000000", 0), ("#FF0000", 0xFF), ("#00FF00", 0xFF00), ("#0000FF", 0xFF0000), ("#2B5748", 0x48572B)],
)
def test_colorref_is_red_green_blue_from_low_to_high_byte(hex_color, value):
    assert theme._colorref(hex_color) == value


def test_window_frame_gets_the_theme_colours(tk_root, monkeypatch):
    import ctypes
    import sys

    calls = []

    class Fake:
        def GetParent(self, _handle):
            return 42

        def DwmSetWindowAttribute(self, hwnd, attribute, value, size):
            calls.append((hwnd, attribute, value._obj.value, size))

    monkeypatch.setattr(ctypes, "windll", type("Windll", (), {"user32": Fake(), "dwmapi": Fake()})(), raising=False)
    theme.apply("aqua")
    calls.clear()  # customtkinter sets its own title bar mode while switching
    theme.paint_window_frame(tk_root)
    size = ctypes.sizeof(ctypes.c_int)
    assert calls == [
        (42, 34, theme._colorref(theme.DEEP), size),  # border
        (42, 35, theme._colorref(theme.BACKGROUND), size),  # caption
        (42, 36, theme._colorref(theme.TEXT), size),  # caption text
    ]
    calls.clear()
    monkeypatch.setattr(sys, "platform", "linux")
    theme.paint_window_frame(tk_root)
    assert calls == []
