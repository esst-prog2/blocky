## Why

A blocked site opens `http://127.0.0.1:8765/blocked?domain=www.reddit.com`, which looks technical and can worry people who do not know what 127.0.0.1 is. The spike `block-page-address` showed that Brave shows `blocky.localhost/reddit.com` cleanly: no warning, no attempt to switch to HTTPS, and the icon in the tab.

## What Changes

- The block page moves to `http://blocky.localhost/<domain>`, for example `blocky.localhost/reddit.com`.
- The app serves pages on port 80 when it is free, so no port shows in the address; when port 80 is taken it uses `blocky.localhost:8765/<domain>`.
- The app keeps listening on `127.0.0.1:8765`, where the extension reads the block list, and tells the extension which page address to use.
- The old address `/blocked?domain=<domain>` sends the browser on to the new one, so an extension that has not been reloaded keeps working.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `block-page`: the block page has a readable address with the blocked domain in it.

## Impact

- `blocky/server.py`: a second listener on port 80 when free, the `/<domain>` page, the redirect from the old address, and `pageOrigin` in `/api/state`.
- `extension/logic.js`, `extension/background.js`: the block page address comes from the app's state instead of being fixed in the extension.
- Tests for the server, the extension and the shared address.
