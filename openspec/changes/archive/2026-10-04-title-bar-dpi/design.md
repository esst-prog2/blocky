## Context

customtkinter makes the process DPI aware when its first window is created (`ScalingTracker.activate_high_dpi_awareness`, called from the `CTk` constructor), with `SetProcessDpiAwareness(2)`: per-monitor v1. A process can set its DPI mode only once; later calls fail and change nothing. Importing customtkinter does not set the mode, so anything that runs before the first window can still choose it. `blocky/__main__.py` creates the window in `main()`, after the administrator check and the background threads; the administrator check can show a message box first. See proposal.md for why v1 is a problem.

## Goals / Non-Goals

**Goals:**
- The real app runs in per-monitor v2 on Windows 10 1703 and later, Windows 11 included.
- A refused or missing call never stops Blocky from starting.

**Non-Goals:**
- Changing customtkinter itself, or its scaling of the window contents.
- Running the test windows in v2: the tests open many windows in one process, which customtkinter has already made v1 by then.

## Decisions

### Set v2 at the very start of `main()`
A new small module `blocky/dpi.py` has one function, `follow_each_monitor() -> bool`, that calls `user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)` (the handle value -4) and returns whether Windows accepted it. `main()` calls it as its first line, before the administrator check, so the message box and the window both get v2, and customtkinter's later v1 call fails harmlessly.

Alternative considered: setting the mode when `blocky/__main__.py` is imported, before `blocky.app`. Rejected: customtkinter only sets its mode when a window is created, so the import order does not matter, and work at import time would also run whenever a test imports `blocky.__main__`.

Alternative considered: calling customtkinter's `deactivate_automatic_dpi_awareness()` and setting the mode ourselves. Rejected: that also switches off customtkinter's scaling of the contents when the window changes monitor, which works today.

### Refusal is silent
On refusal (an older Windows without the function, an `OSError` from the call, or a mode already set) the function returns `False` and Blocky continues with customtkinter's v1, exactly as before this change. There is nothing the user could do about it, so no warning is shown.

### Tests in a separate process
Because a process can set its mode only once, and the test process has already been made v1 by the window tests, the test for the real call runs a short Python child process that calls `follow_each_monitor()`, then creates a customtkinter window, and reports whether the process is still v2. A second test makes the Windows call fail (stubbed) and checks the function returns `False` without raising. A third checks that `main()` calls it before anything else.

## Risks / Trade-offs

- [customtkinter's note that v2 made windows grow on monitors with other scaling] → it concerned windows that cannot be resized; the spike saw no growth with Blocky's resizable window, and the owner checks the real app once on both screens.
- [The font list popup and future popups] → they are placed and sized in the window's own pixels and already handle a monitor change (the DPI test from settings-appearance); they are part of the owner's check.
- [The spike only covered one laptop and one monitor] → a refusal or an unexpected problem only affects the title bar size; rolling back is removing one call.

## Migration Plan

No data changes. Rolling back is removing the call in `main()`.
