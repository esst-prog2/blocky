"""Every text a window or the block page shows, for the tests that pin English and look for leftover English."""

import html
import re
import tkinter
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from blocky import config as config_module
from blocky import server
from blocky.config import Config
from blocky.settings import FOLLOW_WINDOWS, Settings

MONDAY_2PM = datetime(2026, 10, 5, 14, 0)
# A config that fills every tab: sites, suggestions, an override still running and one of each History event.
SAMPLE_EVENTS = [
    {"type": "site_added", "timestamp": "2026-10-04T17:05:00", "item": "reddit.com", "details": ""},
    {"type": "site_edited", "timestamp": "2026-10-04T17:06:00", "item": "x.com", "details": "twitter.com → x.com"},
    {"type": "site_removed", "timestamp": "2026-10-04T17:07:00", "item": "youtube.com", "details": ""},
    {"type": "suggestion_added", "timestamp": "2026-10-04T17:08:00", "item": "Tidy desk", "details": ""},
    {"type": "suggestion_edited", "timestamp": "2026-10-04T17:09:00", "item": "Tidy the desk", "details": ""},
    {"type": "suggestion_removed", "timestamp": "2026-10-04T17:10:00", "item": "Tidy the desk", "details": ""},
    {"type": "schedule_changed", "timestamp": "2026-10-04T17:11:00", "item": "", "details": "Mon–Fri, 09:00–17:00"},
]
SAMPLE_OVERRIDES = [
    {
        "type": "override",
        "domain": "x.com",
        "timestamp": "2026-10-05T13:30:00",
        "reason": "Reading a thread for class",
        "until": "2026-10-05T17:00:00",
    },
    {
        "type": "override",
        "domain": "news.ycombinator.com",
        "timestamp": "2026-10-05T13:00:00",
        "reason": "Job post",
        "until": "2026-10-05T17:00:00",
    },
    {"type": "undo", "domain": "news.ycombinator.com", "timestamp": "2026-10-05T13:10:00"},
]
# Choices that show the most text: Follow Windows opens the dark and light theme rows.
SAMPLE_SETTINGS = (Settings(), Settings(theme=FOLLOW_WINDOWS, time_format="12h"))


def sample_config(settings: Settings) -> Config:
    return Config(
        domains=["reddit.com", "x.com", "news.ycombinator.com"],
        shortlist=["10-minute walk", "Tidy the desk"],
        overrides=[dict(entry) for entry in SAMPLE_OVERRIDES],
        events=[dict(entry) for entry in SAMPLE_EVENTS],
        settings=settings,
    )


def open_sample(open_app, folder: Path, settings: Settings, **kwargs):
    path = folder / "config.yaml"
    config_module.save(path, sample_config(settings))
    app = open_app(path, hosts_path=folder / "hosts", clock=lambda: MONDAY_2PM, **kwargs)
    app.update()
    return app


def _texts_of(widget) -> list[str]:
    if isinstance(widget, ctk.CTkOptionMenu):
        return [widget.get(), *widget.cget("values")]
    if isinstance(widget, ctk.CTkSegmentedButton):
        return []  # its buttons are CTkButtons, found as its children
    if isinstance(widget, ctk.CTkEntry):
        return [widget.cget("placeholder_text") or ""]
    if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton, ctk.CTkCheckBox)):
        return [widget.cget("text")]
    return []


def window_texts(app) -> list[str]:
    """Every label, button, check box, menu and placeholder text in the window, in widget order, without empties."""
    found: list[str] = []

    def walk(widget) -> None:
        found.extend(text for text in _texts_of(widget) if text)
        # Tk's own list: customtkinter hides some inner widgets, such as the tab buttons, from winfo_children.
        for child in tkinter.Misc.winfo_children(widget):
            walk(child)

    walk(app)
    return found


def page_texts(page: str) -> list[str]:
    """The visible text pieces of a block page, plus its lang attribute."""
    lang = re.search(r'<html lang="([^"]*)"', page)
    body = re.sub(r"<style>.*?</style>", "", page)
    pieces = [html.unescape(piece).strip() for piece in re.split(r"<[^>]+>", body)]
    return [f"lang={lang[1] if lang else ''}", *(piece for piece in pieces if piece)]


def sample_pages(state_extra: dict) -> dict[str, list[str]]:
    """The block page while blocked with suggestions, not blocked, and with an empty shortlist."""
    state = {"shortlist": ["10-minute walk"], "blocked": ["reddit.com"], "windowEnd": "17:00", **state_extra}
    return {
        "blocked": page_texts(server.render_blocked(state, "reddit.com")),
        "not blocked": page_texts(server.render_blocked(state, "example.com")),
        "no suggestions": page_texts(server.render_blocked({**state, "shortlist": []}, "reddit.com")),
    }
