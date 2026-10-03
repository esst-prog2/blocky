"""Blocky's look: one dark theme built on the palette 9CB080 / 618764 / 2B5748 / 273338.

Every text colour below has at least 4.5:1 contrast on the surface it is used on,
and input borders at least 3:1, so the window stays readable (WCAG AA).
"""
import customtkinter as ctk

# Palette
SAGE = "#9CB080"
GREEN = "#618764"
DEEP = "#2B5748"
SLATE = "#273338"

# Roles
BACKGROUND = SLATE
CARD = "#2F3E44"  # slate lifted one step, so cards stand out from the background
HOVER = "#35474D"
BORDER = "#7D928A"
TEXT = "#F1F4EC"
MUTED = "#A9B5AD"
SOFT_ON_DEEP = "#C6D3C2"
PRIMARY = SAGE
PRIMARY_HOVER = "#B4C4A2"
ON_PRIMARY = SLATE
DISABLED = "#3A4A4F"
DISABLED_TEXT = "#8A9690"
WARNING = "#E8B85C"
DANGER = "#EE8F7F"

# Spacing (8-point grid) and shape
GAP = 8
PAD = 16
MARGIN = 20
RADIUS = 10
CONTROL_HEIGHT = 36

DISPLAY = "Segoe UI Variable Display"
TEXT_FONT = "Segoe UI Variable Text"
SEMIBOLD = "Segoe UI Variable Text Semibold"


def font(role: str) -> ctk.CTkFont:
    sizes = {
        "display": (DISPLAY, 24, "bold"),
        "title": (SEMIBOLD, 15, "normal"),
        "body": (TEXT_FONT, 13, "normal"),
        "caption": (TEXT_FONT, 12, "normal"),
        "button": (SEMIBOLD, 13, "normal"),
        "brand": (DISPLAY, 20, "bold"),
    }
    family, size, weight = sizes[role]
    return ctk.CTkFont(family=family, size=size, weight=weight)


def card(parent, color: str = CARD, **kwargs) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, fg_color=color, corner_radius=RADIUS, **kwargs)


def label(parent, text: str = "", role: str = "body", color: str = TEXT, **kwargs) -> ctk.CTkLabel:
    options = {"anchor": "w", "justify": "left", **kwargs}
    return ctk.CTkLabel(parent, text=text, font=font(role), text_color=color, **options)


def primary_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=text, command=command, font=font("button"), height=CONTROL_HEIGHT,
        corner_radius=8, fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
        text_color=ON_PRIMARY, text_color_disabled=DISABLED_TEXT, **kwargs,
    )


def quiet_button(parent, text: str, command, color: str = SAGE, **kwargs) -> ctk.CTkButton:
    """A text-only button for secondary or destructive actions."""
    return ctk.CTkButton(
        parent, text=text, command=command, font=font("button"), height=CONTROL_HEIGHT,
        corner_radius=8, fg_color="transparent", hover_color=HOVER,
        text_color=color, text_color_disabled=DISABLED_TEXT, **kwargs,
    )


def set_enabled(button: ctk.CTkButton, enabled: bool) -> None:
    """Enable or disable a button so that the difference is visible, not only its state."""
    if button.cget("fg_color") in (PRIMARY, DISABLED):
        button.configure(fg_color=PRIMARY if enabled else DISABLED)
    button.configure(state="normal" if enabled else "disabled")


def entry_style() -> dict:
    return {
        "height": CONTROL_HEIGHT, "corner_radius": 8, "border_width": 1, "border_color": BORDER,
        "fg_color": BACKGROUND, "text_color": TEXT, "placeholder_text_color": MUTED, "font": font("body"),
    }


def entry(parent, **kwargs) -> ctk.CTkEntry:
    return ctk.CTkEntry(parent, **{**entry_style(), **kwargs})


def option_menu(parent, values: list[str], **kwargs) -> ctk.CTkOptionMenu:
    return ctk.CTkOptionMenu(
        parent, values=values, height=CONTROL_HEIGHT, corner_radius=8, font=font("body"),
        dropdown_font=font("body"), fg_color=BACKGROUND, button_color=BACKGROUND,
        button_hover_color=HOVER, text_color=TEXT, dropdown_fg_color=CARD,
        dropdown_hover_color=DEEP, dropdown_text_color=TEXT, **kwargs,
    )


def checkbox(parent, text: str) -> ctk.CTkCheckBox:
    return ctk.CTkCheckBox(
        parent, text=text, font=font("body"), text_color=TEXT, fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER, border_color=BORDER, checkmark_color=ON_PRIMARY,
        corner_radius=6, border_width=2, width=72,
    )


def textbox(parent, **kwargs) -> ctk.CTkTextbox:
    return ctk.CTkTextbox(
        parent, font=font("body"), fg_color=BACKGROUND, text_color=TEXT, border_width=1,
        border_color=BORDER, corner_radius=8, scrollbar_button_color=DISABLED,
        scrollbar_button_hover_color=BORDER, **kwargs,
    )


def chip(parent, text: str, fg_color: str = BACKGROUND) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent, text=text, font=font("caption"), text_color=TEXT, fg_color=fg_color,
        corner_radius=12, height=26, padx=10,
    )


class Message(ctk.CTkLabel):
    """A hint or error line that takes no space while it is empty."""

    def __init__(self, parent, color: str = MUTED) -> None:
        super().__init__(parent, text="", font=font("caption"), text_color=color, anchor="w", justify="left")
        self._pack_options: dict | None = None

    def pack(self, **options) -> None:
        self._pack_options = options
        self._sync()

    def configure(self, require_redraw: bool = False, **kwargs) -> None:
        super().configure(require_redraw, **kwargs)
        if "text" in kwargs and self._pack_options is not None:
            self._sync()

    def _sync(self) -> None:
        if self.cget("text"):
            super().pack(**self._pack_options)
        else:
            self.pack_forget()


def list_entry_focus(entry: ctk.CTkEntry) -> None:
    """Show a list row's border only while it is being edited."""
    entry.configure(border_color=BACKGROUND)
    entry.bind("<FocusIn>", lambda _event: entry.configure(border_color=BORDER), add="+")
    entry.bind("<FocusOut>", lambda _event: entry.configure(border_color=BACKGROUND), add="+")


def danger_on_hover(button: ctk.CTkButton) -> None:
    """Keep a destructive action quiet until the pointer is on it."""
    button.configure(text_color=MUTED)
    button.bind("<Enter>", lambda _event: button.configure(text_color=DANGER), add="+")
    button.bind("<Leave>", lambda _event: button.configure(text_color=MUTED), add="+")
