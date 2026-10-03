## Why

The shortlist is edited in one free text box, unlike sites, which are added and changed one at a time with checks. The History tab only records overrides, so changes to sites, suggestions and the schedule leave no trace, and its lines are not aligned.

## What Changes

- Suggestions are added one at a time: an add box that only accepts 1 to 120 characters that are not already on the list, and a list whose rows can be edited, saved and removed, like the block list.
- Every change is recorded: sites added, edited and removed; suggestions added, edited and removed; schedule changes; overrides and undos.
- The History tab shows a table with aligned columns (When, Event, Item, Details), newest first.
- Non-override changes are stored in a new `events` list in the config. Overrides stay in `overrides`, which the blocking rules read. A config without `events` loads with an empty list.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `override-history`: the History tab lists every change, in columns, newest first.
- `block-page`: suggestions are added, edited and removed one at a time.

## Impact

- `blocky/config.py`: the `events` list and its checks when loading.
- `blocky/controller.py`: recording events; adding, editing and removing suggestions instead of replacing the whole list; history rows.
- New `blocky/history.py` (event names, dates and schedule descriptions) and `blocky/suggestions.py` (suggestion checks).
- `blocky/app.py`: the Shortlist and History tabs.
- Tests for each of these.
