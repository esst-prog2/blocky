"""Blocky's look: five themes, a font and a text size, applied to the whole window at once.

Every theme gives each text colour at least 4.5:1 contrast on the surfaces it is used on, and input borders and
disabled buttons at least 3:1, so the window stays readable (WCAG AA); tests/test_theme.py checks every pair.
The current theme's colours are module values (theme.BACKGROUND, ...) that `apply` replaces; read them when a
widget is made, never in a default argument, which Python fixes once when this module loads.
"""

import customtkinter as ctk

from blocky import settings as settings_module

ROLES = (
    "BACKGROUND",
    "CARD",
    "HOVER",
    "BORDER",
    "TEXT",
    "MUTED",
    "DEEP",  # status card and selected tab
    "ON_DEEP",
    "SOFT_ON_DEEP",
    "ACCENT",  # brand name and text buttons
    "PRIMARY",
    "PRIMARY_HOVER",
    "ON_PRIMARY",
    "DISABLED",
    "DISABLED_TEXT",
    "WARNING",
    "DANGER",
)

THEMES: dict[str, dict[str, str]] = {
    # Forest: the palette 9CB080 / 618764 / 2B5748 / 273338.
    "forest": {
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
    },
    # Navy: 27374D / 526D82 / 9DB2BF / DDE6ED.
    "navy": {
        "BACKGROUND": "#27374D",
        "CARD": "#2F4159",
        "HOVER": "#384C66",
        "BORDER": "#7D93A5",
        "TEXT": "#DDE6ED",
        "MUTED": "#9DB2BF",
        "DEEP": "#526D82",
        "ON_DEEP": "#FFFFFF",
        "SOFT_ON_DEEP": "#F0F4F7",
        "ACCENT": "#9DB2BF",
        "PRIMARY": "#9DB2BF",
        "PRIMARY_HOVER": "#B7C8D2",
        "ON_PRIMARY": "#27374D",
        "DISABLED": "#3A4C63",
        "DISABLED_TEXT": "#8D9FAE",
        "WARNING": "#E8B85C",
        "DANGER": "#F09A8A",
    },
    # Sand: AD8B73 / CEAB93 / E3CAA5 / FFFBE9, with a terracotta button.
    "sand": {
        "BACKGROUND": "#FFFBE9",
        "CARD": "#FFFDF6",
        "HOVER": "#E3CAA5",
        "BORDER": "#81614B",
        "TEXT": "#2C1F17",
        "MUTED": "#624937",
        "DEEP": "#E3CAA5",
        "ON_DEEP": "#2C1F17",
        "SOFT_ON_DEEP": "#4F3A2C",
        "ACCENT": "#8A3D24",
        "PRIMARY": "#DB8E6E",
        "PRIMARY_HOVER": "#E1A288",
        "ON_PRIMARY": "#2C1F17",
        "DISABLED": "#E3CAA5",
        "DISABLED_TEXT": "#6F5849",
        "WARNING": "#6B4500",
        "DANGER": "#A63A2B",
    },
    # Aqua: E3FDFD / CBF1F5 / A6E3E9 / 71C9CE.
    "aqua": {
        "BACKGROUND": "#E3FDFD",
        "CARD": "#F4FEFE",
        "HOVER": "#CBF1F5",
        "BORDER": "#349298",
        "TEXT": "#0E3235",
        "MUTED": "#247175",
        "DEEP": "#A6E3E9",
        "ON_DEEP": "#0E3235",
        "SOFT_ON_DEEP": "#1C5A5E",
        "ACCENT": "#196C70",
        "PRIMARY": "#71C9CE",
        "PRIMARY_HOVER": "#8BD3D7",
        "ON_PRIMARY": "#0E3235",
        "DISABLED": "#CBF1F5",
        "DISABLED_TEXT": "#387C80",
        "WARNING": "#6B4500",
        "DANGER": "#A63A2B",
    },
    # Blossom: F9F5F6 / F8E8EE / FDCEDF / F2BED1.
    "blossom": {
        "BACKGROUND": "#F9F5F6",
        "CARD": "#FDFBFB",
        "HOVER": "#F8E8EE",
        "BORDER": "#85475E",
        "TEXT": "#2D151E",
        "MUTED": "#663346",
        "DEEP": "#FDCEDF",
        "ON_DEEP": "#2D151E",
        "SOFT_ON_DEEP": "#512938",
        "ACCENT": "#602A3E",
        "PRIMARY": "#F2BED1",
        "PRIMARY_HOVER": "#F4CAD9",
        "ON_PRIMARY": "#2D151E",
        "DISABLED": "#F8E8EE",
        "DISABLED_TEXT": "#724656",
        "WARNING": "#6B4500",
        "DANGER": "#A63A2B",
    },
}

# The current theme's colours; `apply` replaces them.
BACKGROUND = CARD = HOVER = BORDER = TEXT = MUTED = DEEP = ON_DEEP = SOFT_ON_DEEP = ""
ACCENT = PRIMARY = PRIMARY_HOVER = ON_PRIMARY = DISABLED = DISABLED_TEXT = WARNING = DANGER = ""
THEME = "forest"
FONT = "Segoe UI Variable"
SCALE = 1.0

# Spacing (8-point grid) and shape
GAP = 8
PAD = 16
MARGIN = 20
RADIUS = 10
BASE_CONTROL_HEIGHT = 36
BASE_CHIP_HEIGHT = 26
CONTROL_HEIGHT = BASE_CONTROL_HEIGHT
CHIP_HEIGHT = BASE_CHIP_HEIGHT

# Segoe UI Variable has separate families for its optical sizes and weights; the other fonts use bold instead.
DISPLAY = "Segoe UI Variable Display"
TEXT_FONT = "Segoe UI Variable Text"
SEMIBOLD = "Segoe UI Variable Text Semibold"
SIZES = {"display": 24, "title": 15, "body": 13, "caption": 12, "button": 13, "brand": 20}
VARIABLE_ROLES = {
    "display": (DISPLAY, "bold"),
    "title": (SEMIBOLD, "normal"),
    "body": (TEXT_FONT, "normal"),
    "caption": (TEXT_FONT, "normal"),
    "button": (SEMIBOLD, "normal"),
    "brand": (DISPLAY, "bold"),
}
BOLD_ROLES = {"display", "title", "button", "brand"}


def apply(theme: str = "forest", font_name: str = "Segoe UI Variable", text_size: str = "normal") -> None:
    """Make this theme, font and text size current for every widget made from now on."""
    global THEME, FONT, SCALE, CONTROL_HEIGHT, CHIP_HEIGHT
    globals().update(THEMES[theme])
    THEME, FONT, SCALE = theme, font_name, settings_module.TEXT_SIZES[text_size]
    CONTROL_HEIGHT = px(BASE_CONTROL_HEIGHT)
    CHIP_HEIGHT = px(BASE_CHIP_HEIGHT)
    ctk.set_appearance_mode("light" if theme in settings_module.LIGHT_THEMES else "dark")


def px(size: float) -> int:
    """A fixed size scaled with the text size, so larger text is not clipped."""
    return round(size * SCALE)


def font_spec(role: str, font_name: str | None = None) -> tuple[str, int, str]:
    """Family, size and weight of a text role in the given font (the current one by default)."""
    font_name = font_name or FONT
    size = round(SIZES[role] * SCALE)
    if font_name == "Segoe UI Variable":
        family, weight = VARIABLE_ROLES[role]
        return family, size, weight
    return font_name, size, "bold" if role in BOLD_ROLES else "normal"


def font(role: str, font_name: str | None = None) -> ctk.CTkFont:
    family, size, weight = font_spec(role, font_name)
    return ctk.CTkFont(family=family, size=size, weight=weight)


def card(parent, color: str | None = None, **kwargs) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, fg_color=color or CARD, corner_radius=RADIUS, **kwargs)


def label(parent, text: str = "", role: str = "body", color: str | None = None, **kwargs) -> ctk.CTkLabel:
    options = {"anchor": "w", "justify": "left", **kwargs}
    return ctk.CTkLabel(parent, text=text, font=font(role), text_color=color or TEXT, **options)


def primary_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=font("button"),
        height=CONTROL_HEIGHT,
        corner_radius=8,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color=ON_PRIMARY,
        text_color_disabled=DISABLED_TEXT,
        **kwargs,
    )


def quiet_button(parent, text: str, command, color: str | None = None, **kwargs) -> ctk.CTkButton:
    """A text-only button for secondary or destructive actions."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        font=font("button"),
        height=CONTROL_HEIGHT,
        corner_radius=8,
        fg_color="transparent",
        hover_color=HOVER,
        text_color=color or ACCENT,
        text_color_disabled=DISABLED_TEXT,
        **kwargs,
    )


def set_enabled(button: ctk.CTkButton, enabled: bool) -> None:
    """Enable or disable a button so that the difference is visible, not only its state."""
    if button.cget("fg_color") in (PRIMARY, DISABLED):
        button.configure(fg_color=PRIMARY if enabled else DISABLED)
    button.configure(state="normal" if enabled else "disabled")


def entry_style() -> dict:
    return {
        "height": CONTROL_HEIGHT,
        "corner_radius": 8,
        "border_width": 1,
        "border_color": BORDER,
        "fg_color": BACKGROUND,
        "text_color": TEXT,
        "placeholder_text_color": MUTED,
        "font": font("body"),
    }


def entry(parent, **kwargs) -> ctk.CTkEntry:
    return ctk.CTkEntry(parent, **{**entry_style(), **kwargs})


def option_menu(parent, values: list[str], **kwargs) -> ctk.CTkOptionMenu:
    return ctk.CTkOptionMenu(
        parent,
        values=values,
        height=CONTROL_HEIGHT,
        corner_radius=8,
        font=font("body"),
        dropdown_font=font("body"),
        fg_color=BACKGROUND,
        button_color=BACKGROUND,
        button_hover_color=HOVER,
        text_color=TEXT,
        dropdown_fg_color=CARD,
        dropdown_hover_color=DEEP,
        # One colour for every entry, so it must read on both the card and the highlighted (deep) entry.
        dropdown_text_color=ON_DEEP,
        **kwargs,
    )


def checkbox(parent, text: str) -> ctk.CTkCheckBox:
    return ctk.CTkCheckBox(
        parent,
        text=text,
        font=font("body"),
        text_color=TEXT,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        border_color=BORDER,
        checkmark_color=ON_PRIMARY,
        corner_radius=6,
        border_width=2,
        width=px(72),
    )


def textbox(parent, **kwargs) -> ctk.CTkTextbox:
    return ctk.CTkTextbox(
        parent,
        font=font("body"),
        fg_color=BACKGROUND,
        text_color=TEXT,
        border_width=1,
        border_color=BORDER,
        corner_radius=8,
        scrollbar_button_color=DISABLED,
        scrollbar_button_hover_color=BORDER,
        **kwargs,
    )


def scrollable_frame(parent, **kwargs) -> ctk.CTkScrollableFrame:
    return ctk.CTkScrollableFrame(
        parent,
        fg_color="transparent",
        scrollbar_button_color=DISABLED,
        scrollbar_button_hover_color=BORDER,
        **kwargs,
    )


def chip(parent, text: str, fg_color: str | None = None, text_color: str | None = None) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font("caption"),
        text_color=text_color or TEXT,
        fg_color=fg_color or BACKGROUND,
        corner_radius=12,
        height=CHIP_HEIGHT,
        padx=10,
    )


class Message(ctk.CTkLabel):
    """A hint or error line that takes no space while it is empty."""

    def __init__(self, parent, color: str | None = None) -> None:
        super().__init__(parent, text="", font=font("caption"), text_color=color or MUTED, anchor="w", justify="left")
        self._pack_options: dict | None = None

    def pack(self, **options) -> None:
        self._pack_options = options
        self._sync()

    def configure(self, require_redraw: bool = False, **kwargs) -> None:
        super().configure(require_redraw, **kwargs)
        if "text" in kwargs and self._pack_options is not None:
            self._sync()

    def _sync(self) -> None:
        if self._pack_options is None:
            return
        if self.cget("text"):
            super().pack(**self._pack_options)
        else:
            self.pack_forget()


def list_entry_focus(entry: ctk.CTkEntry) -> None:
    """Show a list row's border only while it is being edited."""
    entry.configure(border_color=BACKGROUND)
    border, background = BORDER, BACKGROUND
    entry.bind("<FocusIn>", lambda _event: entry.configure(border_color=border), add="+")
    entry.bind("<FocusOut>", lambda _event: entry.configure(border_color=background), add="+")


def danger_on_hover(button: ctk.CTkButton) -> None:
    """Keep a destructive action quiet until the pointer is on it."""
    button.configure(text_color=MUTED)
    muted, danger = MUTED, DANGER
    button.bind("<Enter>", lambda _event: button.configure(text_color=danger), add="+")
    button.bind("<Leave>", lambda _event: button.configure(text_color=muted), add="+")


def _colorref(hex_color: str) -> int:
    red, green, blue = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return red | green << 8 | blue << 16


def paint_window_frame(window) -> None:
    """Colour the title bar and border on Windows 11; older Windows keeps its own colours."""
    import ctypes
    import sys

    if sys.platform != "win32":
        return
    window.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    for attribute, color in ((34, DEEP), (35, BACKGROUND), (36, TEXT)):  # border, caption, caption text
        value = ctypes.c_int(_colorref(color))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value))


apply()
