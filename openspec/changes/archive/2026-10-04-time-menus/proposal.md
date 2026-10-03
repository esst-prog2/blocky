## Why

Typing a time lets the user enter something invalid and then be told it is wrong. Picking the hour and minute from menus makes an invalid time impossible to enter.

## What Changes

- In the Schedule tab, each of the start and end times is picked with two menus: an hour from 00 to 23 and a minute from 00 to 59. Every minute stays possible, so short test windows such as one ending at 17:58 can still be set.
- The typed time fields are removed, along with the "Use a time like 09:00" message they needed. The app still checks the time when saving.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `schedule`: the typed time-entry requirement is removed and replaced by one for hour and minute menus.

## Impact

- `blocky/app.py`: the Schedule tab's time fields.
- `tests/test_app.py`: the schedule tests use the menus.
