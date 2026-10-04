"""Let Windows fit the whole window, title bar included, to the monitor it is on."""

import ctypes

# DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2: Windows also scales the title bar and frame when the window changes
# monitor. customtkinter sets per-monitor v1 when its first window opens, in which the title bar keeps its size.
PER_MONITOR_AWARE_V2 = -4


def follow_each_monitor() -> bool:
    """Ask Windows for per-monitor v2; whether it was accepted.

    Call it before the first window opens: a process can set its DPI mode only once, so customtkinter's own request
    then has no effect. When Windows refuses (older Windows, or a mode set already), Blocky runs as before.
    """
    try:
        return bool(ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(PER_MONITOR_AWARE_V2)))
    except (AttributeError, OSError):
        return False
