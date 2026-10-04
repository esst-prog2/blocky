import os
import tkinter

import customtkinter as ctk
import pytest
from hypothesis import settings

from blocky import language, theme
from blocky.app import App
from blocky.settings import WindowsTime

# "deep" tries 50x as many inputs per property test; run it now and then with HYPOTHESIS_PROFILE=deep.
settings.register_profile("deep", max_examples=5000)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))


@pytest.fixture(autouse=True)
def default_look():
    # The current theme and language are module state; every test starts and ends with today's look, in English.
    theme.apply()
    language.apply("en")
    yield
    theme.apply()
    language.apply("en")


@pytest.fixture
def open_app():
    # On this machine Tk sometimes cannot read its own library files while a window opens
    # (most likely antivirus scanning them), so opening is retried a few times.
    def open_window(*args, **kwargs):
        # Follow Windows would read this machine's regional settings; tests expect 24-hour time and Monday first
        # unless they choose otherwise (GitHub's Windows runner uses US settings).
        kwargs.setdefault("windows_time", lambda: WindowsTime())
        # Likewise Windows' display language: English unless a test chooses another (the owner's Windows is Dutch).
        kwargs.setdefault("windows_language", lambda: "en")
        for attempt in range(3):
            try:
                return App(*args, **kwargs)
            except tkinter.TclError:
                if attempt == 2:
                    raise

    return open_window


@pytest.fixture
def tk_root():
    # Same retry as open_app: Tk sometimes cannot read its library files while a window opens.
    for attempt in range(3):
        try:
            root = ctk.CTk()
            break
        except tkinter.TclError:
            if attempt == 2:
                raise
    yield root
    root.destroy()
