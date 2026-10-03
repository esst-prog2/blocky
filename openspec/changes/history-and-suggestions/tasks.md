## 1. Data and rules

- [x] 1.1 Add the `events` list to `blocky/config.py`, checked when loading (each entry a section with a type and a valid timestamp), verified by tests that a config without `events` loads and one with a broken entry counts as damaged
- [x] 1.2 Add `blocky/suggestions.py` with the suggestion check and hint, verified by `tests/test_suggestions.py`
- [x] 1.3 Add `blocky/history.py` with event names, the date format and the schedule description, verified by `tests/test_history.py`
- [x] 1.4 Record events in `blocky/controller.py` for sites, suggestions and the schedule; replace `set_shortlist` with add, edit and remove; add `history_rows` merging events and overrides newest first, verified by `tests/test_controller.py`

## 2. Window

- [x] 2.1 Shortlist tab with an add box, hint and list rows, verified by `tests/test_app.py`
- [x] 2.2 History tab as an aligned table, newest first, verified by `tests/test_app.py` and a screenshot
- [x] 2.3 Run the full test suite and ruff, and verify both pass

## 3. Record

- [x] 3.1 Log the change in `PLANNING_LOG.md` and archive this change after a manual check
