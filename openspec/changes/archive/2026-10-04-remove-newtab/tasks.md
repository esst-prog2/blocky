## 1. Code

- [x] 1.1 Remove the `newtab` override from `extension/manifest.json`, delete `extension/newtab.html`, `extension/newtab.js` and `extension/newtab.test.js`, and update `tests/test_extension_files.py` so it checks there is no new-tab override
- [x] 1.2 Remove `render_home` and the `/` route from `blocky/server.py`, and verify with `tests/test_server.py` that `/` now answers 404; move the shortlist check in `tests/test_controller.py` to the block page
- [x] 1.3 Drop "and in new tabs" from the suggestion help text in `blocky/app.py`, and update `README.md` and the manifest description
- [x] 1.4 Run ruff check, ruff format --check, mypy, pytest and the extension tests, and verify all pass

## 2. Record

- [x] 2.1 Log the change in `PLANNING_LOG.md`, archive this change and update the browser-extension spec's purpose line
