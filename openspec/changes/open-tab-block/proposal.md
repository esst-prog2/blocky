## Why

A tab on a blocked site that was already open when a window started keeps working. Moving between pages inside it (for example between posts on reddit) does not start a new navigation, so the extension does not redirect it. A reload is already blocked, because it is a new navigation. This gap lets the block be bypassed inside an open tab.

## What Changes

- The extension redirects a tab when the page changes inside a blocked site during an active block window, not only when a new navigation starts.
- When a block window starts, the extension redirects any open tab that is on a blocked site to the block page.
- Ordinary tabs are not affected.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `browser-extension`: the redirect requirement extends to in-page navigation and to open tabs when a window starts.

## Impact

- `extension/background.js`: a listener for in-page navigation, and a periodic check of open tabs.
- `extension/manifest.json`: the `alarms` permission is needed for the periodic check.
- Must be verified in Brave: that in-page navigation fires the listener on reddit, and that the open-tab check redirects an open reddit tab when a window starts.
