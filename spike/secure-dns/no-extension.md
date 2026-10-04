# Secure DNS without the extension (rerun, 2026-10-05)

Asked for in the review of 2026-10-04: with the extension redirecting on onBeforeNavigate, the first run (on.md, off.md) no longer tested the hosts file. This rerun had Blocky's extension **turned off**, so only the hosts file blocked. Normal Brave profile, block window active, all ten domains on the block list. Checklist: `spike/review-reruns-checklist.md`.

**Question:** does Brave reach any of the ten domains, with secure DNS on (Cloudflare) and off?
**Pass:** none of the ten loads the real site (Brave's error page, or the site's own offline page) in either setting, and wikipedia.org loads.

| Domain | Secure DNS on (Cloudflare) | Secure DNS off |
|---|---|---|
| nos.nl | blocked, ERR_CONNECTION_REFUSED | blocked, ERR_CONNECTION_REFUSED |
| nu.nl | blocked, ERR_QUIC_PROTOCOL_ERROR then ERR_CONNECTION_REFUSED | blocked, ERR_CONNECTION_REFUSED |
| reddit.com | blocked, ERR_CONNECTION_REFUSED | blocked, ERR_CONNECTION_REFUSED |
| x.com | blocked, ERR_CONNECTION_REFUSED | blocked, ERR_CONNECTION_REFUSED |
| youtube.com | blocked, ERR_CONNECTION_REFUSED | blocked, YouTube's own offline page ("Maak verbinding met internet") |
| chess.com | blocked, ERR_CONNECTION_REFUSED | blocked, ERR_CONNECTION_REFUSED |
| manners.nl | blocked, ERR_CONNECTION_REFUSED | blocked, ERR_CONNECTION_REFUSED |
| temu.com | blocked, Blocky's own server answered (http, 404 page) | blocked, Blocky's own server answered (http, 404 page) |
| hardverapro.hu | blocked, Blocky's own server answered (http, 404 page) | blocked, ERR_CONNECTION_REFUSED (https) |
| linkedin.com | blocked, ERR_QUIC_PROTOCOL_ERROR | blocked, ERR_CONNECTION_REFUSED |
| wikipedia.org (control) | loads | loads |

**Answer: pass.** Real sites reached: **0 of 10 with secure DNS on, 0 of 10 with it off**. Brave's secure DNS does not get past the hosts file.

Notes:

- The "on" column comes from the console run (spike hw4-console), which already had secure DNS on; that run did not clear the cache first, but every site gave an error, so none came from the cache. Before the "off" run, cached images and files of the last hour were cleared.
- temu.com and hardverapro.hu were opened over plain http when Brave had no https history for them; that request reached Blocky's own server on port 80 (the block page address since 2026-10-04), which answers `/` with a 404. Still blocked; showing the block page there instead is a possible later improvement.
- youtube.com's service worker answered with YouTube's offline page in the "off" run but not in the "on" run; either way the real site did not load.
- ERR_QUIC_PROTOCOL_ERROR: Brave first tried HTTP/3, which it remembers for those sites, and that failed against 127.0.0.1 as well.
