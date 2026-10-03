## 1. Code

- [x] 1.1 Add the `alarms` permission to `extension/manifest.json`, and verify the manifest still parses with `node --test extension/logic.test.js` and the Python extension tests
- [x] 1.2 Add a `webNavigation.onHistoryStateUpdated` listener in `extension/background.js` that redirects a blocked hostname during an active window, reusing the same state check
- [x] 1.3 Add a one-minute `chrome.alarms` sweep in `extension/background.js` that redirects open tabs on blocked hostnames during an active window
- [x] 1.4 Verify with `node --test extension/logic.test.js` that the shared rules still pass, and extend them for the sweep decision if one is added to `extension/logic.js`

## 2. Brave verification

- [x] 2.1 Reload the extension, start Blocky, and verify an open `reddit.com` tab moved between posts is redirected to the block page
- [x] 2.2 Verify a `reddit.com` tab opened before a window starts is redirected within about a minute of the start
- [x] 2.3 Verify a tab on an ordinary site is unaffected during an active window
- [x] 2.4 Verify a reload of `reddit.com` still shows the block page

## 3. Record

- [x] 3.1 Log the Brave results in `PLANNING_LOG.md`
- [x] 3.2 Archive this change once the verification passes
