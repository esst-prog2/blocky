# Normal profile results

| Domain | Event fired | Error string | Service worker registered | Page seen |
|---|---|---|---|---|
| nonexistent-test-blocky.example (control) | yes | net::ERR_NAME_NOT_RESOLVED | not checked | Brave error page |
| reddit.com | yes (https://www.reddit.com/) | net::ERR_CONNECTION_REFUSED | yes, the site's own sw.js for www.reddit.com (not Blocky's) | Blocky block page |
| nos.nl | yes (https://nos.nl/) | net::ERR_CONNECTION_REFUSED | no | Blocky block page |
| nu.nl | yes (https://www.nu.nl/) | net::ERR_CONNECTION_REFUSED | yes, the site's own service-worker.js for www.nu.nl (not Blocky's) | Blocky block page |
| x.com | yes (https://x.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| youtube.com | no (no line in the console after a clear) | none | yes, YouTube's own sw.js for www.youtube.com, fetch handler present | YouTube's own offline page |
| chess.com | yes (https://chess.com/) | net::ERR_CONNECTION_REFUSED | yes, the site's own fcm-worker.js for www.chess.com (not Blocky's) | Blocky block page |
| manners.nl | yes (https://manners.nl/) | net::ERR_CONNECTION_REFUSED | yes, the site's own superpwa-sw.js for www.manners.nl, fetch handler present (not Blocky's) | Blocky block page |
| temu.com | yes (http://temu.com/) | net::ERR_CONNECTION_REFUSED | yes, the site's own sw.js for www.temu.com, fetch handler present (not Blocky's) | Blocky block page |
| hardverapro.hu | yes (https://hardverapro.hu/) | net::ERR_CONNECTION_REFUSED | yes, the site's own static/sw.js for hardverapro.hu, no fetch handler (not Blocky's) | Blocky block page |
| linkedin.com | yes (https://www.linkedin.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |

## Console lines (rerun, 2026-10-05)

`console-normal.txt` holds the console lines for the control and all ten domains, as asked in the review of 2026-10-04 (the first version had only the control's line). They were recorded again because the extension no longer logs them: since the HW4 spike it redirects when a navigation starts, before any error. Setup: Blocky's extension turned off, `spike/console-logger` loaded (it logs the same `onErrorOccurred` line and redirects nothing), normal profile, block window active.

How to read the file, in order:

- Lines 1 to 38: the visits with secure DNS on (Cloudflare), the "on" run of `secure-dns/no-extension.md`. Lines 39 to 64: the same domains with secure DNS off, starting with reddit.com.
- The number after the address is the frame: `0` is the page itself; other numbers are frames inside a page and are not visits. `drive.google.com` and `sites.google.com/view/temubv` came from the address bar turning "temu" into a search; the `linkedin.com/tscp-serving`, `li.protechts.net` and `cs.ns1p.net` lines are trackers Brave's shields blocked (`ERR_BLOCKED_BY_CLIENT`).
- Each refused page is followed by one or more `ERR_ABORTED` lines for the same address as Brave stops the attempt.
- temu.com (both runs) and hardverapro.hu (secure DNS on) have no line: they were opened over http and reached Blocky's own server on port 80, which answered with a 404 page.
- youtube.com: refused like the others with secure DNS on; with it off, only an `ERR_ABORTED` for www.youtube.com, while YouTube's own offline page was shown (its service worker answering, as in the HW4 spike).

Compared with the HW4 table above: the same nine domains give `ERR_CONNECTION_REFUSED` (or `ERR_QUIC_PROTOCOL_ERROR` first, for nu.nl and linkedin.com), and the control gives `ERR_NAME_NOT_RESOLVED`. youtube.com now sometimes gets refused instead of always being answered by its service worker.
