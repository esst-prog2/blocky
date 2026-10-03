## Why

Blocking distracting websites currently means editing the Windows hosts file by hand, with no schedule, no reason logging, and no way to get through a block deliberately. This change delivers the first useful version of Blocky: a desktop app that manages a block list and weekly schedule, writes the hosts file itself, and offers a logged override and a suggestion shortlist.

## What Changes

- Add a desktop app (Python, customtkinter) for managing the block list, the schedule, the override, the status panel, and the override history.
- Add background blocking that writes and removes `127.0.0.1` hosts-file entries as the schedule opens and closes, and cleans up stale entries.
- Add a local HTTP server in the app that serves the blocked-site page with the shared suggestion shortlist.
- Add a Brave (Chromium) extension that replaces the new-tab page with the shortlist and redirects a tab to the blocked-site page when a blocked navigation fails.
- Each block-list entry also blocks its `www.` variant.
- The schedule is one time range applied to the selected weekdays.
- An override lasts until the current scheduled block window ends.
- The app runs elevated from the start so hosts-file writes never need a mid-session UAC prompt.

## Capabilities

### New Capabilities

- `block-list`: add, edit, and remove blocked domains; validate entries and reject malformed ones; apply the `www.` variant.
- `schedule`: one weekly time range on selected weekdays, with a single unnamed "Schedule".
- `hosts-blocking`: write and remove hosts-file entries from the block list and schedule, including cleanup of leftover entries; runs elevated.
- `manual-override`: pick a currently blocked domain, require a reason, unblock it until the current block window ends, and log domain, timestamp, and reason.
- `override-history`: a history tab listing past overrides.
- `status-panel`: show which domains are blocked and the time remaining until the next change.
- `block-page`: a local server that serves the blocked-site page with the shared shortlist, and the shortlist defined once in the app.
- `browser-extension`: a Brave extension that replaces the new-tab page and redirects blocked navigations to the block page, reading the block list and shortlist from the app's local server.

### Modified Capabilities

None (no existing specs).

## Impact

- New Python application with a customtkinter UI, a YAML config file, a background checker, and a local HTTP server.
- Writes to `C:\Windows\System32\drivers\etc\hosts`, which requires elevation.
- A Brave extension (Chromium, Manifest V3) loaded unpacked in developer mode.
- The blocked-site page is available only while the app is running.

## Later Levels

Not part of this change; each becomes its own future change:

- Per-day schedule ranges or several time windows per day.
- Hosting the block page on a Raspberry Pi or in the cloud (blocking stays local).
- Blocking specific pages or paths rather than whole domains.
- Multiple named schedule profiles.
- Per-site suggestion lists.
- Running as a persistent background service that survives reboot.
- Blocking other subdomains such as `m.youtube.com` automatically.
- Usage analytics beyond the override log.
- macOS and Linux support.
