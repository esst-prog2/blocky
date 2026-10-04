## 1. Server

- [x] 1.1 Let `Server` also listen on `127.0.0.1:80` when free, falling back to 8765 only, and expose `page_origin`; verify with tests for both cases (port free; port taken by another socket) and that both listeners are bound to 127.0.0.1
- [x] 1.2 Serve the block page at `/<domain>`, redirect `/blocked?domain=<domain>` to `<pageOrigin>/<domain>`, and add `pageOrigin` to `/api/state`; verify with server tests, including an escaped domain and that `/` still answers 404

## 2. Extension

- [x] 2.1 Build the block page address from `state.pageOrigin` in `extension/logic.js` and `background.js`, and update the extension tests and the shared-address test; verify with `node --test` and pytest

## 3. Checks and record

- [x] 3.1 Run ruff check, ruff format --check, mypy, pytest and the extension tests, and verify all pass
- [x] 3.2 Manual check by the owner: after reloading the extension, a blocked site opens at `blocky.localhost/<domain>` in Brave
- [x] 3.3 Log the change in `PLANNING_LOG.md`, update the README and archive this change
