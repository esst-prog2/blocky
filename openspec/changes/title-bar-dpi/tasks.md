## 1. DPI mode

- [x] 1.1 Add `blocky/dpi.py` with `follow_each_monitor()` that asks Windows for per-monitor v2 and returns whether it was accepted, returning `False` (never raising) when the function is missing or the call fails; verify with a test that stubs the Windows call to fail, to be missing and to raise, and with a test in a child process that the mode is v2 after the call and stays v2 after a customtkinter window is created
- [x] 1.2 Call it as the first line of `main()` in `blocky/__main__.py`; verify with a test that `main()` calls it before the administrator check, and that Blocky still starts when it returns `False`
- [x] 1.3 After the owner's check showed a visible resize while moving between screens: let customtkinter check the monitor scaling every 30 ms instead of 100 ms, set in `main()` right after the DPI mode, so the contents catch up sooner; verify with a test that the interval is 30 ms and that `main()` sets it before the administrator check, and by the owner comparing the move between screens

## 2. Checks and record

- [x] 2.1 Run ruff check, ruff format --check, mypy, pytest and the extension tests and verify all pass
- [ ] 2.2 Manual check by the owner with the real app (`pythonw -m blocky`): the title bar has the right size on the laptop screen and the external monitor, moving between them, resizing, maximising and restoring behave normally, and the font list and a theme change work on the external monitor
- [ ] 2.3 Log the decisions in `PLANNING_LOG.md` and archive this change
