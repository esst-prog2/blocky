## Why

During an active window the status panel reads "Blocking active — … remaining" even when nothing is blocked, because every domain is overridden or the block list is empty. The code review found this misleading.

## What Changes

- During an active window with no blocked domains, the panel reads "Window active, nothing blocked — 3h 00m remaining" instead of "Blocking active — 3h 00m remaining".
- Outside a window and with at least one blocked domain, the text is unchanged.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `status-panel`: the status text distinguishes an active window with blocked domains from one with none.

## Impact

- `blocky/rules.py`: `status_text`.
- `tests/test_rules.py`: tests for an empty list and for all domains overridden.
