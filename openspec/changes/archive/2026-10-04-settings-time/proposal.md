## Why

Blocky shows every time in 24-hour notation and every week starting on Monday. People who read the clock in 12-hour notation, or whose week starts on Sunday or Saturday, have to translate in their heads. This is part 2 of the Settings feature, and both settings follow Windows' own regional settings until the user chooses, so most people never need to touch them.

## What Changes

- A **Language and time** section in the Settings tab, below Appearance, with two settings:
  - **Time format**: Follow Windows (default), 24-hour (17:00) or 12-hour (5:00 PM).
  - **First day of the week**: Follow Windows (default), Monday, Saturday or Sunday.
- **12-hour time everywhere a clock time is shown**: the "unblocked until" lines on the Status tab, the History tab (when and schedule details), the block page, and the schedule fields, where the hour runs from 1 to 12 with an AM/PM switch next to it. Durations such as "3h 00m remaining" do not change, and the stored schedule stays in 24-hour form.
- **First day of the week** sets the order of the day boxes on the Schedule tab and of days in schedule descriptions on the History tab (with Sunday first, Sunday to Tuesday is "Sun–Tue").
- **History formats when it is shown**: new schedule changes are stored as days and times instead of finished text, so a later change of format also changes earlier entries. Entries stored as text by earlier versions are read back where they follow the known pattern, and shown as stored otherwise.
- **Reset to default** puts both back to Follow Windows. The part of the Reset requirement about Start with Windows is removed, because that setting moved to a later installer level.

## Capabilities

### New Capabilities

### Modified Capabilities
- `settings`: new requirements for the time format and the first day of the week, how they follow Windows, and where they apply; the Reset to default requirement is replaced by one without the Start with Windows exception and with the time settings added.

## Impact

- `blocky/settings.py`: two new fields with defaults, choices and fallback; reading Windows' short time format and first day of the week.
- `blocky/history.py`: time and day formatting take the settings; schedule changes stored as data.
- `blocky/controller.py`: records schedule changes as days and times.
- `blocky/timefield.py`: an hour from 1 to 12 with an AM/PM switch in 12-hour mode.
- `blocky/app.py`: the new section; the day boxes in the chosen order; times on the Status and History tabs.
- `blocky/server.py`, `blocky/__main__.py`: the block page shows the end time in the chosen format; the state the extension reads keeps its 24-hour `windowEnd`.
- Tests for each of these. No change to the extension or to stored schedules.
