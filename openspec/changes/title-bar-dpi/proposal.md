## Why

When Blocky's window moves from the laptop screen (300 %) to an external monitor with lower scaling, its contents rescale but the title bar keeps the laptop's size, so it looks heavily zoomed in. customtkinter makes the process per-monitor DPI aware in version 1, in which Windows does not rescale the title bar. The spike `spike/title-bar-dpi` showed that per-monitor version 2 fixes the title bar on the owner's two screens without other problems.

## What Changes

- Blocky starts in per-monitor v2 DPI mode, set before customtkinter loads, so Windows sizes the title bar and window frame for the monitor the window is on.
- If Windows refuses v2 (older Windows, or a mode already set), Blocky starts as it does today, with customtkinter's own mode, and does not report an error.
- The spike's `run.py` stays as the record of the check; Blocky itself no longer needs it.

## Capabilities

### New Capabilities
- `display-scaling`: the window, including its title bar, fits the scaling of the monitor it is on, also after it moves to another monitor.

### Modified Capabilities

## Impact

- `blocky/__main__.py`: sets the DPI mode at the very start, before `blocky.app` (and with it customtkinter) is imported.
- A small new module for the DPI call, so the startup order is explicit and testable.
- Tests: the mode is per-monitor v2 after startup, and a refused call leaves startup working.
- No change to settings, the block page, the extension or stored data. Windows 11 is the target; on older Windows the behaviour stays as today.
