## Context

Clock times are formatted in four places, each with `%H:%M`: `history.when()` and `history.describe_schedule()` (History tab), `App._render_released` (Status tab), and `rules.snapshot()["windowEnd"]`, which the block page shows and the extension only tests for being set. Day names come from `DAYS` in `app.py` and `DAY_NAMES` in `history.py`, always Monday first; weekdays are stored as 0 (Monday) to 6 (Sunday). A schedule change is recorded in `config.events` with its details as finished text ("Mon–Fri, 09:00–17:00"). `TimeField` holds two boxes, hour 0–23 and minute 0–59, and returns "HH:MM". Settings live in `blocky/settings.py`; the window redraws on every settings change (part 1). On the owner's machine Windows has `sShortTime = HH:mm` and `iFirstDayOfWeek = 0` under `HKCU\Control Panel\International`.

## Goals / Non-Goals

**Goals:**
- One place that turns a time or a set of weekdays into text, used by the window, the History and the block page.
- Earlier History entries follow a later change of setting.

**Non-Goals:**
- Changing how schedules, overrides or events are stored, apart from adding fields to new schedule events.
- Date formats per language (part 3), or the language of day and month names.
- Noticing a change of Windows' regional settings while Blocky is open; it is read again at the next start or settings change.

## Decisions

### A `TimeStyle` and a small formatting module
New `blocky/clock.py` holds `TimeStyle(twelve_hour: bool, first_day: int)` (a frozen dataclass, first day 0–6 as in the stored weekdays) and pure functions: `format_time(hour, minute, style)` ("17:00" or "5:00 PM", no leading zero in 12-hour form, as Windows does), `day_order(style)`, `describe_days(weekdays, style)` and `describe_schedule(weekdays, start, end, style)`. `history.when()` and the Status lines call it. The name `TimeStyle` avoids a clash with `Controller.clock`, which returns the current time.

Alternative considered: Python's `%I:%M %p`. Rejected: it pads the hour ("05:00 PM") and follows the C locale.

### Settings and Windows
`Settings` gains `time_format` (`follow-windows`, `24h`, `12h`) and `first_day` (`follow-windows`, `monday`, `saturday`, `sunday`), checked per field like the others, so configs from part 1 load with both at Follow Windows. `windows_time()` in `settings.py` reads `sShortTime` (12-hour when it has `h` and no `H`) and `iFirstDayOfWeek` (0 Monday to 6 Sunday), falling back to 24-hour and Monday when either cannot be read. `time_style(settings, windows)` is pure, like `effective_theme`, so every combination is tested without the registry. The window reads Windows' values at start and before every redraw.

Only Monday, Saturday and Sunday are offered as choices because they are the first days used around the world; Follow Windows still honours any day Windows is set to.

### History formats when it is shown
`Controller.set_schedule` records `weekdays`, `start` and `end` in the event next to `details`. `details` stays, so an older Blocky reading the config still shows something. `history.rows()` takes the `TimeStyle` and builds the details from the fields when present. For older entries it parses `details` with the pattern the earlier code produced (day names, ranges joined by `–`, or "no days", then `, HH:MM–HH:MM`); text that does not match is shown as stored. The config check for events is unchanged (only `type` and `timestamp` are required).

### Days in the chosen order
`day_order(style)` lists the seven weekday numbers starting at `first_day`. The Schedule tab builds its boxes in that order and keeps each box's weekday number, so saving stores the same numbers as before. `describe_days` groups runs of three or more days that follow each other in that order, so with Sunday first, Sunday to Tuesday is "Sun–Tue"; with Monday first the same days are "Mon, Tue, Sun" as today.

### 12-hour schedule fields
In 12-hour mode `TimeField` shows an hour box from 1 to 12 and an AM/PM switch (a two-choice segmented button) after the minutes; `get()` still returns 24-hour "HH:MM" (12 AM is 00, 12 PM is 12). Stepping the hour wraps from 12 to 1 without flipping AM/PM, as in Windows' own time fields. Switching the format redraws the window, so the fields are rebuilt from the saved schedule; unsaved edits in the fields are lost, as with any settings change.

### The block page
`page_state()` in `__main__.py` adds `"timeStyle": {"twelveHour": ..., "firstDay": ...}` next to `appearance`; `render_blocked` formats `windowEnd` with it. `windowEnd` itself stays "HH:MM", so the extension and the `/api/state` contract do not change.

### The Settings tab
A second section, Language and time, under Appearance, with two rows of the same choice buttons as the text size. A short line under each row names what Windows uses now, for example "Windows uses 24-hour time." and "Windows starts the week on Monday.", so the user sees what Follow Windows gives. (First planned inside the Follow Windows button, which cut the text off in the four-button row.)

## Risks / Trade-offs

- [An older details text with an unexpected shape] → shown as stored; the parser only reformats exact matches, covered by a property test that any text either round-trips or comes back unchanged.
- [Windows set to a first day other than Monday, Saturday or Sunday] → Follow Windows uses it; it cannot be picked by hand, which is acceptable.
- [The AM/PM switch is one more control in a narrow row] → it scales with the text size like the other fixed sizes; checked at Extra large.

## Migration Plan

Configs from part 1 get both new settings at Follow Windows. Old schedule events keep their text and are reformatted when they match. An older Blocky reading a newer config ignores the new fields.
