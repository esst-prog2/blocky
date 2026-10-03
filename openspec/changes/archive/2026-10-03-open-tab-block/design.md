## Context

The early redirect (see `openspec/changes/archive/2026-10-03-early-block-redirect`) listens for `webNavigation.onBeforeNavigate`. That covers new page loads, including reloads, which are already blocked. It does not cover moves inside a page, which do not start a new navigation, nor tabs that were open before a window started.

## Goals / Non-Goals

**Goals:**
- Redirect in-page moves on blocked sites during an active window.
- Redirect open tabs on blocked sites when a window starts.

**Non-Goals:**
- Stopping a page that is already loaded from fetching content in the background.
- Changing the hosts-file blocking.

## Decisions

**Watch in-page moves with `webNavigation.onHistoryStateUpdated`.** Single-page sites such as reddit change pages with the browser history API, which fires this event. Alternative: check on every page load, which would miss moves in the page.

**Sweep open tabs with `chrome.alarms`, once a minute.** Each sweep queries all tabs, asks the app for its state, and redirects tabs on blocked hostnames. This matches the app's own one-minute check. Alternative: keep a timer in the service worker, which Chromium can stop while idle, so an alarm is more reliable.

**Reuse the same state check and the same blocked-hostname rule.** The extension still keeps no cache, so the state is fetched at each check.

## Risks / Trade-offs

- **The sweep runs at most once a minute, so an open tab can stay up for up to a minute after a window starts.** This matches the app's delay and is accepted.
- **A page that is already loaded can keep fetching content after the redirect.** Mitigation: the redirect replaces the page, so the user sees the block page.
- **`chrome.alarms` needs the `alarms` permission.** Mitigation: the permission is added to the manifest, and checked in Brave.

## Verification

In Brave, with the app running and the window active:
- An open `reddit.com` tab moved between posts is redirected to the block page.
- A `reddit.com` tab opened before a window starts is redirected within about a minute.
- A tab on an ordinary site is unaffected.
