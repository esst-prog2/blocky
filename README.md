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
in between   a background checker compares the current time against the
             schedule; it adds or removes hosts-file entries as
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
- A live status panel showing which domains are currently blocked and the time left until the block window ends (outside a window it says no blocking is active)
- A manual override: pick a domain, type a required reason, and it's unblocked until the current scheduled block window ends — logged with domain, timestamp, and reason. The override can be undone at any time, which re-blocks the domain at once; the history keeps the override line and adds an "override undone" line
- A history tab listing past overrides
- A shared shortlist of productive suggestions, defined once in the app, shown on the block page served by the app; a Brave extension sends the tab there whenever a blocked domain is requested
**Not this term:**
- Blocking specific pages/paths rather than whole domains (the hosts file only knows domains; it would need a proxy, or an extension that blocks by itself, which Blocky's does not)
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
- Given a blocked domain requested while its block window is active, Brave with Blocky's extension loaded displays the local block page with the shared suggestion shortlist, rather than the browser's error page. This includes `youtube.com`, whose own offline page used to appear first; the extension now redirects as soon as the navigation starts (see section 5). Without the extension, Brave shows its own error page, and the site is still blocked.
- Given a malformed domain entered into the block list (e.g. missing a dot, containing spaces), the app rejects it with an error message and never writes it to the hosts file.
## 5. What could stop this
 
- **Admin privileges.** Editing `C:\Windows\System32\drivers\etc\hosts` requires elevated rights. Blocky relaunches itself elevated when it starts, which shows one UAC prompt per start; after that it writes the hosts file without further prompts (spike 1.1). The prompt on every start is kept on purpose until an installer can avoid it (`docs/installer-level.md`). Declining the prompt shows a message that Blocky needs administrator rights.
- **Domain-level blunt blocking.** This blocks whole domains, not specific pages, and doesn't reliably handle sites served across many IPs/CDNs without extra care.
- **HSTS-preloaded sites.** Reddit and YouTube are HSTS-preloaded, so browsers never send them as plain HTTP, and Blocky cannot answer them with its own page through the hosts file. The block page therefore relies on the Brave extension, which sends a blocked site to it as soon as the navigation starts. It used to wait for the connection to fail, but YouTube's own service worker answered first with its offline page (spike 1.2 and the HW4 spike), so the extension no longer waits (early-block-redirect). Tested in Brave, the redirect works for both sites.
- **Not tamper-proof by design.** Since I'm the same user with admin rights, I could edit the hosts file directly and bypass the tool entirely. That's acceptable here — the point is friction and logging, not enforcement — but worth stating plainly. Closing Blocky also removes its entries, so closing it during a window unblocks every site until it is started again. The other way round, restarting or shutting down Windows with Blocky open leaves its entries in place, so sites stay blocked, also after the window ends, until Blocky is started again; if the window has ended by then, it removes them within about 30 seconds (spike p1-lifecycle). Blocky does handle Windows' end-of-session notice, but at three real restarts Windows did not let that cleanup run. A cleanup at boot is planned for the installer level.
- **Other browsers.** Blocking is at the system level, so Firefox and Edge are blocked too, but they show their own "can't connect" page rather than Blocky's. Only Brave with the extension shows the block page. Tested with default settings and no extension. Private windows are blocked too, but do not show the block page, since the extension does not run in them by default.
- **Subdomains.** The hosts file blocks each domain and its www. variant only. In Brave, the extension also sends any subdomain (such as old.reddit.com or music.youtube.com) to the block page. Without the extension (in other browsers, private windows, or with it disabled) subdomains load normally.
- **Timing.** The app checks once a minute, so blocking starts between 0 and 60 seconds after a window opens. In five tests it took 46 seconds, and in a later test 5 seconds.
- **Sleep.** When the PC wakes during an active window with Blocky open, its entries are back in the hosts file within 38 seconds, averaging 12 seconds across five cycles. When a window ends while the PC sleeps, the entries are gone 10 to 25 seconds after waking (three cycles, spike p1-lifecycle).
- **IP addresses, secure DNS and VPNs.** Typing a blocked site's IP address didn't load the real site in five tests. With Brave's secure DNS on (Cloudflare) or off, none of ten blocked sites got past the hosts file, also with the extension turned off (`spike/secure-dns/no-extension.md`). Firefox's secure DNS (Cloudflare, at both Increased and Max Protection) did not get past it either, for five blocked sites (spike p1-manual). With Surfshark on, in a normal and a private window, none of five got past the block. These VPN results cover one Surfshark connection, so other VPNs may behave differently.
- **Other programs in the hosts file.** Blocky only changes the lines between its own `# BEGIN BLOCKY` and `# END BLOCKY` markers, so lines from other programs, such as Docker Desktop's, stay as they are. Just before writing, it reads the file again, and if another program wrote it in the meantime, it starts from that version, so the other program's new lines are not overwritten (spike p1-lifecycle).
- **A damaged config.** If `config.yaml` cannot be read (not valid YAML, empty, or with sections of the wrong kind), Blocky keeps it under a new name (`config.yaml.damaged-<date and time>`), starts with an empty list and says so in the window; a single invalid domain is skipped with a warning instead (spike p1-config).
- **Moving between monitors.** When the window moves to a monitor with other scaling, Windows resizes the title bar and frame at once, and the contents follow a moment later with a short fade while customtkinter redraws them. This only happens while crossing between screens. Checking for the change more often (every 30 ms instead of 100 ms) made it look worse, so it stays as it is.
- **Data/privacy.** All data is local config: my own block list, schedule, shortlist, settings, and the history, including the reasons I type for overrides. Nothing leaves the machine and no third-party data is involved, so the full real setup can be shown in class.
## Tech
 
Python, with a `customtkinter` UI for a modern look with minimal setup overhead. A local HTTP server in the app serves the block page with the shortlist at `blocky.localhost/<domain>` (port 80 when it is free, otherwise `blocky.localhost:8765`); a Brave extension (Chromium, Manifest V3) redirects blocked requests to it. Config (block list, schedule, shortlist, overrides, history and settings) is stored as YAML in `%APPDATA%\Blocky\config.yaml` but never hand-edited — all changes go through the app. Failures of the background check, a damaged config and errors while closing are also written to `errors.log` in the same folder.

The Settings tab changes how Blocky looks: five themes (Forest and Navy are dark; Sand, Aqua and Blossom are light) or Follow Windows, which uses a chosen dark and light theme to match Windows' app mode; ten fonts that come with Windows; and four text sizes. Changes show at once, also on the block page, and are saved in the `settings` section of the config. Reset to default puts every setting back, to Forest, Segoe UI Variable and Normal, and the time format, first day of the week and language to Follow Windows, with Undo. The colours are in `blocky/theme.py`; `tests/test_theme.py` checks their contrast. After changing a theme's colours, redraw the icons with `.venv\Scripts\python tools\make_icons.py` (needs Pillow: `.venv\Scripts\python -m pip install pillow`).

Under Language and time, the time format (24-hour, or 12-hour such as 5:00 PM) and the first day of the week (Monday, Saturday or Sunday) follow Windows' regional settings until you choose. The time format applies to the Status and History tabs, the block page and the schedule fields, which get an AM/PM switch; the first day sets the order of the days on the Schedule tab and in History. Windows' settings are read when Blocky starts and when a setting changes. The schedule is always stored in 24-hour form.

Blocky speaks English, Dutch and Hungarian. The Language setting, also under Language and time, follows Windows' display language until you choose: Dutch or Hungarian when Windows uses one of them, in any region, and English otherwise. The language applies to the whole window, the History tab (event names, days and dates, also for earlier entries), the block page and the administrator message at start; `errors.log` stays English. The texts are in `blocky/language.py`, keyed by the English text, and the date formats in `blocky/clock.py`. `tests/test_translations.py` fails when a text has no Dutch or Hungarian entry. `.venv\Scripts\python tools\translation_review.py <file.md>` writes all three languages side by side for checking.

Some things wait for a later installer level: starting without UAC prompts and with Windows, removing leftover blocking at boot, and a guard against running Blocky twice. They are collected in `docs/installer-level.md`.

## Running it

1. Install Python 3.11 or newer. Keep the project outside OneDrive or other synced folders: syncing interferes with git and with Blocky's own file writes.
2. From the repo folder, create a virtual environment and install the dependencies:
   `python -m venv .venv` and then `.venv\Scripts\python -m pip install -r requirements.txt`.
3. Start the app with `.venv\Scripts\pythonw -m blocky`. Windows asks for administrator rights, because the app edits the hosts file. Accept the prompt.
4. Load the browser extension: open `brave://extensions`, turn on Developer mode, click "Load unpacked", and select the `extension` folder.

Use `.venv\Scripts\python -m blocky` instead of `pythonw` to see error messages in a console window. Run the tests with `.venv\Scripts\python -m pytest`. The tests that open a real window take most of the 6 to 10 minutes the full suite needs; `.venv\Scripts\python -m pytest -m "not window"` skips them and runs the rest in about half a minute, which suits quick checks while working. Run the full suite before pushing. The extension has its own tests, which need Node.js 22 or newer: `node --test "extension/*.test.js"`.

To see which lines the tests never run, use `.venv\Scripts\python -m coverage run --branch --source=blocky -m pytest` and then `.venv\Scripts\python -m coverage report -m`. For the extension, add `--experimental-test-coverage` to the `node --test` command.

`tests/test_properties.py` holds property tests: Hypothesis tries 100 generated inputs per rule on every run. To search harder (5000 inputs per rule, a few minutes), set `HYPOTHESIS_PROFILE=deep` before running pytest.

Check style and types with `.venv\Scripts\python -m ruff check .`, `.venv\Scripts\python -m ruff format --check .` and `.venv\Scripts\python -m mypy`; their settings are in `pyproject.toml`. GitHub runs all of these checks and both test suites on Windows for every push (`.github/workflows/checks.yml`).

To start Blocky from the Start menu or the taskbar, run `powershell -ExecutionPolicy Bypass -File tools\create_shortcut.ps1` once. It adds a Blocky shortcut with Blocky's icon to the Start menu; right-click it there and choose **Pin to taskbar**.

The icon is drawn by `tools/make_icons.py`, in each theme's colours, and it writes every size used by the app, the block page and the extension. Run `.venv\Scripts\python tools\make_icons.py` after changing it (it needs Pillow, see the Settings paragraph above).

Mutation testing checks the tests themselves: `.venv\Scripts\python tools\mutation_test.py` makes small changes to the code (with cosmic-ray, installed separately with `.venv\Scripts\python -m pip install cosmic-ray`) and lists every change no test noticed. It takes up to an hour, edits files in `blocky/` while it runs (so do not edit them meanwhile; it restores them when it stops), and keeps its results in `.mutation/`; add `--report` to show results without running. A stopped run resumes from those results, so after changing a module, delete its `.mutation/<module>.sqlite` first, or the old results are shown again.
