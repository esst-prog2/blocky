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
