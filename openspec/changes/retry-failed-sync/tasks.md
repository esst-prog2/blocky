## 1. Code

- [x] 1.1 Add a test to `tests/test_checker.py` in which the first hosts update fails, and verify the entries appear within seconds; confirm it fails before the change
- [x] 1.2 Make `Checker.run` in `blocky/checker.py` wait `RETRY_INTERVAL` (5 seconds) after a failed check and the normal interval after a successful one
- [x] 1.3 Run ruff check, ruff format --check, mypy, pytest and the extension tests, and verify all pass

## 2. Record

- [ ] 2.1 Log the change in `PLANNING_LOG.md` and archive this change
