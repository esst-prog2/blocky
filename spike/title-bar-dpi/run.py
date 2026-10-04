"""Open Blocky's window in one DPI mode, to compare the title bar on two monitors.

Usage, from the repository root (no administrator rights needed; it uses a throwaway config and hosts file):
    .venv\\Scripts\\python spike\\title-bar-dpi\\run.py v1     what Blocky does today (customtkinter's default)
    .venv\\Scripts\\python spike\\title-bar-dpi\\run.py v2     per-monitor v2, which lets Windows scale the title bar

The mode must be set before customtkinter is imported: once a process has a DPI mode, Windows refuses to change it,
so customtkinter's own call (per-monitor v1) then has no effect.
"""

import ctypes
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2

mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode not in ("v1", "v2"):
    sys.exit("Give the mode: v1 or v2")
if mode == "v2" and not ctypes.windll.user32.SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2):
    sys.exit("Windows refused per-monitor v2")

from blocky import config as config_module  # noqa: E402
from blocky.app import App  # noqa: E402
from blocky.config import Config  # noqa: E402

folder = Path(tempfile.mkdtemp())
config_module.save(folder / "config.yaml", Config(domains=["reddit.com"], shortlist=["10-minute walk"]))
app = App(folder / "config.yaml", hosts_path=folder / "hosts")
app.title(f"Blocky (DPI mode {mode})")
user32 = ctypes.windll.user32
user32.GetThreadDpiAwarenessContext.restype = ctypes.c_void_p
current = ctypes.c_void_p(user32.GetThreadDpiAwarenessContext())
is_v2 = bool(user32.AreDpiAwarenessContextsEqual(current, PER_MONITOR_AWARE_V2))
print(f"Mode {mode}: per-monitor v2 is {'on' if is_v2 else 'off'}")
app.mainloop()
