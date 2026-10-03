## 1. Code

- [x] 1.1 Change `status_text` in `blocky/rules.py` to return "Window active, nothing blocked — <remaining> remaining" when the window is active and no domain is blocked, and verify with `python -m pytest -q`
- [x] 1.2 Add tests in `tests/test_rules.py` for an empty block list and for every domain overridden, and verify the existing "Blocking active" test still passes

## 2. Record

- [x] 2.1 Log the change in `PLANNING_LOG.md` and archive this change
