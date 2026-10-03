# Blocky
 
A small Windows desktop app that blocks distracting websites on a schedule I set — showing a shortlist of more productive things to do instead — with a manual override for when I genuinely need to get through. No editing config files by hand, no digging through the Windows hosts file.
 
## 1. The demo
 
I open the app. It shows my block list (`reddit.com`, `youtube.com`, `x.com`) and the current schedule — Mon–Fri 09:00–17:00 — with the status panel reading **"Blocking active — 3h 00m remaining"**, since it's 14:00 on a Tuesday. I try to open reddit.com anyway; instead of a broken connection, the Brave extension sends the tab to a local page served by the app: "reddit.com is blocked until 17:00" with a shortlist underneath — *read tomorrow's lecture notes, 10-minute walk*. I click **Override** in the app, type a reason ("checking a work thread"), and reddit.com unblocks — the panel now reads **"reddit.com unblocked until 17:00"** with a countdown. Switching to the History tab, I see the override logged with the domain, timestamp, and my reason.
 
## 2. The shape
 
```
in           a block-list + weekly schedule + a shared shortlist of productive
             suggestions, entered through the app's UI
out          an updated Windows hosts file + a local page shown in the browser
             when a blocked site is requested + a live status display in the
             app + an override log
in between   a background checker compares the current time against each
             domain's schedule; it adds or removes hosts-file entries as
             windows open and close, points blocked domains at a small local
             web server that serves the block page with the suggestion
             shortlist, and temporarily exempts a domain when I override it,
             logging the reason
```
 
## 3. The size
 
**First useful version:**
- Add, edit, and remove blocked domains through a text input in the UI; each entry also blocks its www. variant
- Define a weekly schedule: one time range that applies to the block list on the days I select
- A background check (roughly once a minute) compares the clock against the schedule and writes/removes entries in the Windows hosts file accordingly
- A live status panel showing which domains are currently blocked and time remaining until the next change
- A manual override: pick a domain, type a required reason, and it's unblocked until the current scheduled block window ends — logged with domain, timestamp, and reason. The override can be undone at any time, which re-blocks the domain at once; the history keeps the override line and adds an "override undone" line
- A history tab listing past overrides
- A shared shortlist of productive suggestions, defined once in the app, shown on a local page served by the app; a Brave extension sends the tab there whenever a blocked domain is requested or a new tab is opened
**Not this term:**
- Blocking specific pages/paths rather than whole domains (would need a proxy or browser extension)
- Multiple named schedule profiles (e.g. "Study Mode" vs "Deep Work") — one active schedule only
- Per-site suggestion lists — one shared shortlist covers every block for now
- Per-day schedule ranges or several time windows per day
- Hosting the block page on a Raspberry Pi or in the cloud (blocking stays local)
- Running as a persistent background service that survives a reboot without me relaunching it
- Any tamper-resistance — since I have admin rights on my own machine, I can always edit the hosts file back myself; this tool isn't meant to be uncircumventable
- macOS/Linux support
- Usage analytics beyond the raw override log (e.g. "you tried to visit reddit.com 4 times this week")
## 4. How we would know it works
 
- Given a domain on the block list and the current time inside its scheduled window, the Windows hosts file contains a `127.0.0.1` redirect entry for that domain.
- Given an override submitted with a reason for a currently-blocked domain, the hosts file entry for that domain is removed, and the history log gains an entry with the domain, timestamp, and reason.
- Given the current time outside the scheduled window for a domain, the hosts file contains no entry for that domain — including cleaning up any leftover entry from before the schedule changed.
- Given a blocked domain requested while its block window is active, Brave displays the local block page with the shared suggestion shortlist, rather than the browser's error page. Known exception: `youtube.com` shows YouTube's own "connection failed" page instead. This limitation is accepted.
- Given a malformed domain entered into the block list (e.g. missing a dot, containing spaces), the app rejects it with an error message and never writes it to the hosts file.
## 5. What could stop this
 
- **Admin privileges.** Editing `C:\Windows\System32\drivers\etc\hosts` requires elevated rights. The app needs to either run elevated from the start or trigger a UAC prompt — The app runs elevated from the start; whether that is smoother than a UAC prompt in customtkinter is still to be tested in a spike.
- **Domain-level blunt blocking.** This blocks whole domains, not specific pages, and doesn't reliably handle sites served across many IPs/CDNs without extra care.
- **HSTS-preloaded sites.** Reddit and YouTube are HSTS-preloaded, so browsers never send them as plain HTTP. The block page therefore relies on the Brave extension reacting to the failed connection, not on HTTP. This is unverified until tested in Brave.
- **Not tamper-proof by design.** Since I'm the same user with admin rights, I could edit the hosts file directly and bypass the tool entirely. That's acceptable here — the point is friction and logging, not enforcement — but worth stating plainly.
- **Other browsers.** Blocking is at the system level, so Firefox and Edge are blocked too, but they show their own "can't connect" page rather than Blocky's. Only Brave with the extension shows the block page. Tested with default settings and no extension.
- **Timing.** Blocking starts about 46 seconds after a window opens, since the app checks once a minute. A window can therefore take up to a minute to start blocking.
- **Sleep.** When the PC wakes during an active window with Blocky open, its entries are back in the hosts file within 38 seconds, averaging 12 seconds across five cycles.
- **IP addresses and secure DNS.** Typing a blocked site's IP address didn't load the real site in five tests. With Brave's secure DNS on (Cloudflare), none of ten blocked sites got past the block.
- **Data/privacy.** All data is local config (my own block list and schedule) with no personal or sensitive third-party data involved, so the full real setup can be shown in class.
## Tech
 
Python, with a `customtkinter` UI for a modern look with minimal setup overhead. A local HTTP server in the app serves the shortlist and block page; a Brave extension (Chromium, Manifest V3) redirects blocked requests and replaces the new-tab page. Config (block list + schedule) is stored as YAML under the hood but never hand-edited — all changes go through the app.

## Running it

1. Install Python 3.11 or newer, then install the dependencies from the repo folder: `pip install -r requirements.txt`.
2. Start the app with `pythonw -m blocky`. Windows asks for administrator rights, because the app edits the hosts file. Accept the prompt.
3. Load the browser extension: open `brave://extensions`, turn on Developer mode, click "Load unpacked", and select the `extension` folder.

Use `python -m blocky` instead of `pythonw` to see error messages in a console window.
