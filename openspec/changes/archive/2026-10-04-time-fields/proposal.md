## Why

The hour and minute menus force a valid time but are long and awkward: the minute menu has 60 entries. A compact field that refuses invalid typing gives the same guarantee with less clutter.

## What Changes

- Each schedule time is a pair of small boxes, `HH : MM`.
- Only digits are accepted, at most two, and only values that fit (hour 00 to 23, minute 00 to 59); other keystrokes are ignored.
- The arrow keys and the mouse wheel step the value up or down, wrapping around.
- Leaving a box pads a single digit (`9` becomes `09`); leaving it empty puts back the previous value.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `schedule`: the menu requirement is replaced by one for guarded time fields.

## Impact

- New `blocky/timefield.py` with the field and its typing rules; `blocky/app.py` uses it.
- New `tests/test_timefield.py`; `tests/test_app.py` types into the fields.
