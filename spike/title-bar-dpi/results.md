# Title bar on a second monitor: results

Run by the owner on 2026-10-04 with the laptop screen (300 %) and an external monitor with lower scaling.

| Mode | Title bar on the external monitor | Resizing, maximising, restoring | Other problems |
|---|---|---|---|
| v1 (today) | stays at the laptop's size, too big | normal | none |
| v2 | right size for the monitor | normal | none |

Answer: pass. Per-monitor v2 fixes the title bar, and the window behaves as in v1. The growth that customtkinter warns about for v2 did not appear; Blocky's window can be resized, and customtkinter only saw it with windows that cannot.
