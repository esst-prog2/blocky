import ctypes
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from blocky import dpi

ROOT = Path(__file__).resolve().parent.parent


class User32:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def SetProcessDpiAwarenessContext(self, context):
        self.calls.append(context.value)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def with_user32(monkeypatch, user32):
    monkeypatch.setattr(ctypes, "windll", type("Windll", (), {"user32": user32})(), raising=False)


def test_accepted_request_asks_for_per_monitor_v2(monkeypatch):
    user32 = User32(1)
    with_user32(monkeypatch, user32)
    assert dpi.follow_each_monitor() is True
    assert user32.calls == [ctypes.c_void_p(-4).value]  # the handle -4, read back as an unsigned pointer


def test_refused_request_returns_false(monkeypatch):
    with_user32(monkeypatch, User32(0))
    assert dpi.follow_each_monitor() is False


@pytest.mark.parametrize("error", [OSError("access denied"), AttributeError("no such function")])
def test_failing_request_returns_false_without_raising(monkeypatch, error):
    with_user32(monkeypatch, User32(error))
    assert dpi.follow_each_monitor() is False


def test_older_windows_without_the_function_returns_false(monkeypatch):
    with_user32(monkeypatch, object())
    assert dpi.follow_each_monitor() is False


def test_mode_is_per_monitor_v2_and_stays_so_after_a_window_opens():
    # A process can set its DPI mode only once, and this test process has it set already, so check in a new one.
    script = textwrap.dedent(
        """
        import ctypes
        from blocky import dpi

        def is_v2():
            user32 = ctypes.windll.user32
            user32.GetThreadDpiAwarenessContext.restype = ctypes.c_void_p
            current = ctypes.c_void_p(user32.GetThreadDpiAwarenessContext())
            return bool(user32.AreDpiAwarenessContextsEqual(current, ctypes.c_void_p(dpi.PER_MONITOR_AWARE_V2)))

        accepted = dpi.follow_each_monitor()
        after_call = is_v2()
        import customtkinter
        window = customtkinter.CTk()  # customtkinter asks for per-monitor v1 here
        window.update()
        after_window = is_v2()
        window.destroy()
        print(accepted, after_call, after_window)
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=ROOT, capture_output=True, text=True, timeout=60, check=True
    )
    assert result.stdout.split() == ["True", "True", "True"]


@pytest.mark.parametrize("accepted", [True, False])
def test_main_asks_for_the_mode_before_anything_else(monkeypatch, accepted):
    import blocky.__main__ as startup

    steps: list[str] = []

    def step(name, result):
        def record():
            steps.append(name)
            return result

        return record

    monkeypatch.setattr(dpi, "follow_each_monitor", step("dpi", accepted))
    monkeypatch.setattr(startup, "is_admin", step("admin check", False))
    monkeypatch.setattr(startup, "relaunch_as_admin", step("relaunch", True))
    startup.main()
    # A refused mode changes nothing: startup goes on to the administrator check either way.
    assert steps == ["dpi", "admin check", "relaunch"]
