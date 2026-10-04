# Block page address check: results

Checked on 2026-10-04 in Brave on the owner's Windows 11 machine, with the mock server in `serve.py`.

| # | Check | Result |
|---|---|---|
| 1 | Open `http://blocky.localhost/reddit.com` | Loads; the address bar shows `blocky.localhost/reddit.com` with the grey info symbol, no "Not secure" label |
| 2 | Icon in the tab | The Blocky icon is shown |
| 3 | Link from another page | Loads, same address |
| 4 | Redirect by script, as the extension does | Loads, same address |
| 5 | Fallback port 8766 | Loads; the address bar shows `blocky.localhost:8766/reddit.com` |

`requests.log` (agent): every page request arrived with `Host: blocky.localhost` on port 80 (or `blocky.localhost:8766`), the favicon was fetched each time, and there was no connection on port 443, so Brave never tried HTTPS.

Answer: yes. Brave resolves `blocky.localhost` to this computer by itself, treats it as a local address (no HTTPS attempt, no warning), and hides `http://` and port 80. Pass on all five checks.
