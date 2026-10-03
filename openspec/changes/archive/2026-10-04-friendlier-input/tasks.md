## 1. Code

- [x] 1.1 Reduce a pasted web address to its domain in `blocky/domains.py` before validation, with tests in `tests/test_domains.py` for a full address, an address with a port, and an address whose host is not valid
- [x] 1.2 Add `parse_time` to `blocky/schedule.py` (accepts `H:MM` and `HH:MM`, returns `HH:MM`, otherwise raises "Use a time like 09:00") with tests in `tests/test_schedule.py`
- [x] 1.3 Use `parse_time` and the at-least-one-weekday rule in `Controller.set_schedule`, with tests in `tests/test_controller.py`, and verify a config file with no weekdays still loads
- [x] 1.4 Run the full test suite and ruff, and verify both pass

## 2. Record

- [x] 2.1 Log the change in `PLANNING_LOG.md` and archive this change
