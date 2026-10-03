## Context

The HW4 spike (see `spike/normal-profile.md` and `spike/fresh-profile.md`) found that nine of ten tested domains fire `onErrorOccurred` and show Blocky's page. `youtube.com` does not fire the event in the normal profile, where YouTube's service worker is registered, and shows YouTube's offline page instead.

## Goals / Non-Goals

**Goals:**
- Redirect blocked navigations regardless of the site's service worker.
- Keep the same blocked hostnames and schedule rules as the hosts file.

**Non-Goals:**
- Changing the hosts-file blocking, which still prevents loading when the extension is off.
- Publishing the extension or changing the block page.

## Decisions

**Listen for `webNavigation.onBeforeNavigate` and redirect with `chrome.tabs.update`.** The event fires before the request is made, so a site's service worker cannot answer first. Alternative: `declarativeNetRequest` redirect rules, which act at the network layer. Rejected for now, since rules would need to be synchronised with the schedule; it can be reconsidered if the listener proves unreliable.

**Check the app's state at navigation time.** The same `fetchState` call as today keeps the block list and window in one place.

## Risks / Trade-offs

- **`onBeforeNavigate` may fire for subframes or for pages the browser then cancels.** Mitigation: filter to the main frame (`frameId === 0`), as the current listener does.
- **The redirect may fire on the block page's own navigation.** Mitigation: the block page is served from `127.0.0.1`, which is not on the block list.
- **Redirecting before the request means the app must be reachable at navigation time.** Mitigation: if the app is closed, the state fetch fails and the navigation proceeds, as it does today.

## Verification

Before the change is accepted, test in Brave with the app running and the schedule active:
- `reddit.com`, `x.com`, `nos.nl`, and `chess.com` show the block page.
- `youtube.com` shows the block page, not YouTube's offline page.
- An ordinary site loads normally.
- With the app closed, a blocked site shows the browser's normal error page.
