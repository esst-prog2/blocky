"""Which texts in a window are shown narrower than they need, so part of them is cut off."""

import tkinter

import customtkinter as ctk


def cut_off(app, tab: str) -> list[str]:
    """Texts of mapped buttons, check boxes and labels on a tab (and the tab row) that are narrower than they ask for."""
    app.select_tab(tab)
    app.update()
    found: list[str] = []

    def walk(widget) -> None:
        if isinstance(widget, (ctk.CTkButton, ctk.CTkCheckBox, ctk.CTkLabel)) and widget.winfo_ismapped():
            text = widget.cget("text")
            if text and widget.winfo_width() < widget.winfo_reqwidth():
                found.append(text)
        for child in tkinter.Misc.winfo_children(widget):
            walk(child)

    walk(app)
    return found


def tabs_fit(app) -> bool:
    """Whether the row of tab buttons fits inside the window."""
    buttons = list(app.tabs._segmented_button._buttons_dict.values())
    right = max(button.winfo_rootx() + button.winfo_width() for button in buttons)
    return right <= app.winfo_rootx() + app.winfo_width()
