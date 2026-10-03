## Why

Three inputs in the window are needlessly unfriendly: a pasted web address such as `https://reddit.com/r/all` is rejected, a time typed as `9:00` is rejected with Python's raw error message, and a schedule with no weekdays is saved although it never applies, so nothing is ever blocked without any sign.

## What Changes

- A pasted web address is reduced to its domain before it is checked: the scheme, port, path, query and fragment are removed.
- Times in the schedule are accepted as `H:MM` or `HH:MM` and stored as `HH:MM`; anything else is rejected with the message "Use a time like 09:00".
- Saving a schedule with no weekdays selected is rejected with the message "Pick at least one day".

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `block-list`: entries may be pasted web addresses, which are reduced to their domain.
- `schedule`: time entry format and the at-least-one-weekday rule.

## Impact

- `blocky/domains.py`: address clean-up before validation.
- `blocky/schedule.py` and `blocky/controller.py`: time parsing and the weekday rule when saving from the window. A saved config with no weekdays still loads, so an existing file is never treated as damaged.
- Tests in `tests/test_domains.py`, `tests/test_schedule.py` and `tests/test_controller.py`.
