## Why

The extension currently redirects a blocked site only after Brave reports the navigation as failed. The HW4 spike found that this misses `youtube.com`: YouTube's own service worker answers the request with its offline page, so no failure is reported and Blocky's page never appears. Reacting when the navigation starts avoids that dependency.

## What Changes

- The extension redirects a tab to the block page when a navigation to a blocked hostname starts during an active block window, instead of waiting for `onErrorOccurred`.
- The redirect applies to the same hostnames as the hosts file, including the `www.` variant.
- Ordinary navigations are not affected.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `browser-extension`: the requirement that redirects a blocked navigation changes from "fails" to "starts".

## Impact

- `extension/background.js`: the listener changes from `webNavigation.onErrorOccurred` to `webNavigation.onBeforeNavigate`.
- `extension/manifest.json`: permissions are unchanged, since `webNavigation` covers both events.
- Must be verified in Brave before it is accepted, since the spike did not test this listener.
