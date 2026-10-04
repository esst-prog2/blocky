# Title bar on a second monitor

Question: does Blocky's title bar match each monitor's scaling if the app uses per-monitor v2 DPI mode instead of customtkinter's default (per-monitor v1), without breaking the rest of the window?

Background: today the title bar keeps the laptop's size (300 %) when the window moves to a monitor with other scaling, while the contents rescale. customtkinter chose v1 because v2 made windows that cannot be resized grow on a monitor with other scaling. Blocky's window can be resized, so v2 may work.

Setup: laptop screen and external monitor with different scaling, both connected. Run each mode from the repository root; it opens Blocky's window with a throwaway config (no administrator rights, the real hosts file is not touched):

- `.venv\Scripts\python spike\title-bar-dpi\run.py v1`
- `.venv\Scripts\python spike\title-bar-dpi\run.py v2`

Do the steps below for v1 first (to see today's behaviour), then for v2:

| # | Do this | Note what you see |
|---|---|---|
| 1 | Start the window on the laptop screen | Title bar and contents normal size? |
| 2 | Drag the window to the monitor | Title bar the right size for the monitor? Contents the right size? Does the window grow, shrink or jump? |
| 3 | On the monitor, resize the window by its edge, then maximise it and restore it | Does it behave normally? |
| 4 | On the monitor, open Settings and the font list | Is the list as wide as its button, four rows tall? |
| 5 | Change the theme on the monitor | Does the window redraw normally? |
| 6 | Drag the window back to the laptop screen | Title bar and contents back to normal? Any growth or jump? |

Pass (v2 replaces v1 in Blocky): in v2, step 2 and 6 show a title bar of the right size on both screens, and steps 2 to 6 show no growth, shrinking, jumps or wrong sizes that v1 does not also show. Fail: any of those holds only for v2.
