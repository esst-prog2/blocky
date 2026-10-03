## 1. Code

- [x] 1.1 Change the listener in `extension/background.js` from `onErrorOccurred` to `onBeforeNavigate`, keeping the main-frame filter, and verify with `node --test extension/logic.test.js` that the logic tests still pass
- [x] 1.2 Remove the temporary `console.log` line from the listener, and verify it no longer appears in the service worker console

## 2. Brave verification

- [x] 2.1 Reload the extension in `brave://extensions`, start Blocky, and verify `reddit.com`, `x.com`, `nos.nl`, and `chess.com` show the block page
- [x] 2.2 Verify `youtube.com` shows the block page, not YouTube's offline page
- [x] 2.3 Verify an ordinary site loads normally during an active window
- [x] 2.4 Verify with Blocky closed that a blocked site shows the browser's normal error page

## 3. Record

- [ ] 3.1 Record the Brave results in `spike/` or the change folder, and log the outcome in `PLANNING_LOG.md`
- [ ] 3.2 Archive this change once the verification passes
