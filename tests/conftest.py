import os
import tkinter

import customtkinter as ctk
import pytest
from hypothesis import settings

from blocky import theme
from blocky.app import App

# "deep" tries 50x as many inputs per property test; run it now and then with HYPOTHESIS_PROFILE=deep.
settings.register_profile("deep", max_examples=5000)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))


@pytest.fixture(autouse=True)
def default_look():
    # The current theme is module state; every test starts and ends with today's look.
    theme.apply()
    yield
    theme.apply()


@pytest.fixture
def open_app():
    # On this machine Tk sometimes cannot read its own library files while a window opens
    # (most likely antivirus scanning them), so opening is retried a few times.
    def open_window(*args, **kwargs):
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
