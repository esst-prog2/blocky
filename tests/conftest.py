import tkinter

import pytest

from blocky.app import App


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
