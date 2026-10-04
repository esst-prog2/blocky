## 0. Layout tweak requested before building

- [x] 0.1 Put Text size next to Font when both fit in full (font button 220 wide, choice buttons sized to their text), and below it otherwise, so no button text is cut off; verify with window tests for side by side at Normal and Large, stacked at the smallest size with Normal and with Verdana at Extra large, after a window resize, and that every size button shows its full text

## 1. Formatting

- [x] 1.1 Add `blocky/clock.py` with `TimeStyle`, `format_time`, `day_order`, `describe_days` and `describe_schedule`; verify with tests for every hour in both formats (00:00 as 12:00 AM, 12:00 as 12:00 PM, 17:05 as 5:05 PM), every first day, and runs across the end of the week ("Sun–Tue" with Sunday first, "Mon, Tue, Sun" with Monday first)
- [x] 1.2 Pin today's output: a test that with 24-hour time and Monday first, `history.when()` and the schedule descriptions give exactly what they give before this change; verify it fails when one is changed

## 2. Settings

- [x] 2.1 Add `time_format` and `first_day` to `Settings` with Follow Windows as default and per-field fallback, `windows_time()` reading `sShortTime` and `iFirstDayOfWeek` (24-hour and Monday when unreadable), and `time_style(settings, windows)`; verify with tests for every combination, for faked registry values (`HH:mm`, `H:mm`, `h:mm tt`, `hh:mm tt`, first days 0 to 6) and for unreadable values, and that a part-1 config loads with both at Follow Windows

## 3. History

- [x] 3.1 Record `weekdays`, `start` and `end` in new schedule events next to `details`, and let `history.rows()` take a `TimeStyle` and build schedule details from the fields, or from older `details` text that follows the earlier pattern; verify with tests for new events, old matching text in both formats, non-matching text shown as stored, and a property test that any text either reformats to the same days and times or comes back unchanged

## 4. Window

- [x] 4.1 Give `TimeField` a 12-hour mode (hour 1–12, AM/PM switch, `get()` still 24-hour); verify with tests that 12:30 AM gives 00:30, 12:30 PM gives 12:30, 5:30 PM gives 17:30, that a saved 00:00 shows as 12:00 AM, and that stepping wraps from 12 to 1
- [x] 4.2 Add the Language and time section with both settings, a line under each row naming Windows' current value; build the day boxes in the chosen order and show times on the Status and History tabs in the chosen format; verify with window tests that each choice changes the window at once, is saved and kept after reopening, that saving the schedule with Sunday first stores the same weekdays, that Reset puts both back to Follow Windows, and that the Settings tab still scrolls to its last row at Extra large and the smallest size

## 5. Block page

- [x] 5.1 Pass the time style to the block page and show the end time in it, keeping `windowEnd` 24-hour in `/api/state`; verify with server tests in both formats and the existing extension tests

## 6. Checks and record

- [x] 6.1 Run ruff check, ruff format --check, mypy, pytest and the extension tests and verify all pass
- [x] 6.2 Run `tools/mutation_test.py` on `clock` and `settings` (add `clock` to its module list) and add tests for real gaps
- [x] 6.3 Manual check by the owner: both settings in the window and on the block page, Follow Windows after changing Windows' time format and first day (then restarting Blocky), typing a 12-hour schedule, and Reset to default
- [x] 6.4 Log the decisions in `PLANNING_LOG.md`, update the README, and archive this change
