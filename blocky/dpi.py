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


# How often customtkinter checks whether the window's monitor scaling changed (its default is 100 ms). Windows resizes
# the frame at once when the window crosses to another monitor; the sooner customtkinter notices, the shorter the
# moment in which the contents still have the old size.
MONITOR_CHECK_MS = 30


def notice_monitor_changes_sooner() -> None:
    from customtkinter.windows.widgets.scaling.scaling_tracker import ScalingTracker

    ScalingTracker.update_loop_interval = MONITOR_CHECK_MS
