## Why

The extension replaces every new tab with "Try something else" and the shortlist. That assumes each new tab is a distraction, even when it was opened for something useful or outside block hours, and it hides Brave's own new tab (search box, shortcuts). When Blocky is closed, every new tab says Blocky is not running. The suggestions are only relevant when the user actually tries a blocked site, and the block page already shows them then.

## What Changes

- **BREAKING** The extension no longer replaces the new-tab page; Brave's own new tab comes back.
- The app's page at `/` ("Try something else"), which only the new tab opened, is removed and now answers 404 like any unknown path.
- The shortlist is shown on the block page only.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `browser-extension`: the new-tab requirement is removed; the loaded-unpacked and extension-disabled scenarios no longer mention the new tab.
- `block-page`: the shortlist is shown on the block page only.

## Impact

- `extension/manifest.json`, `extension/newtab.html`, `extension/newtab.js`, `extension/newtab.test.js`: the new-tab override and its page and tests are removed.
- `blocky/server.py`: `render_home` and the `/` route are removed.
- `blocky/app.py`: the suggestion help text no longer mentions new tabs.
- `tests/test_server.py`, `tests/test_controller.py`, `tests/test_extension_files.py`, `README.md`: updated to match.
