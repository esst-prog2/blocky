## Context

The extension reads the state from `http://127.0.0.1:8765/api/state` and sends blocked tabs to `http://127.0.0.1:8765/blocked?domain=<domain>`; both addresses are fixed in `extension/logic.js` (`APP_ORIGIN`), and a test checks that this matches the server's host and port. The spike `block-page-address` confirmed that Brave resolves `blocky.localhost` to this machine by itself and treats it as local.

## Goals / Non-Goals

**Goals:** a readable block page address; no change in how reliably the extension finds the app; extensions that have not been reloaded keep working.

**Non-Goals:** HTTPS; changing the state address; a hosts entry for `blocky.localhost` (browsers resolve `.localhost` themselves).

## Decisions

### The state address stays fixed; the page address comes from the app
The extension keeps fetching `http://127.0.0.1:8765/api/state`, and the state gains `pageOrigin`: `http://blocky.localhost` when the app got port 80, otherwise `http://blocky.localhost:8765`. The extension builds the block page address from that. The choice between port 80 and the fallback is made once, in the app, which is the only side that knows whether port 80 was free.

Alternative considered: the extension trying port 80 and then 8765 itself. Rejected: two fixed addresses in the extension, an extra request on every navigation while port 80 is taken, and the same decision made in two places.

### Two listeners, one handler
`Server` binds `127.0.0.1:8765` as today and also tries `127.0.0.1:80`; an `OSError` there (port in use, or not allowed) leaves only the 8765 listener. Both use the same handler. Both bind to `127.0.0.1` only, as the existing localhost test requires.

### Page paths
`/<domain>` serves the block page when the path is a single segment containing a dot; `/api/state` and `/favicon.ico` are matched first. `/` and other paths answer 404 as today. `/blocked?domain=<domain>` answers 302 with `Location: <pageOrigin>/<domain>`, the domain lower-cased and percent-encoded.

## Risks / Trade-offs

- [Blocky holds port 80 while it runs, so a web server started later cannot use it] → Blocky only takes port 80 when it is free at start; a developer who needs port 80 can start their server first.
- [Another browser does not resolve `.localhost` names] → Chromium-based browsers and Firefox do; the extension only runs in Brave.

## Migration Plan

After updating, reload the extension in `brave://extensions`. Until then the old extension still works, through the redirect from `/blocked?domain=`.
