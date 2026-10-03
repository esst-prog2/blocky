# Fresh profile results

Fresh profile: started with `--user-data-dir` pointing at a new folder, with only the Blocky extension loaded.

| Domain | Event fired | Error string | Service worker registered | Page seen |
|---|---|---|---|---|
| youtube.com | yes (https://youtube.com/) | net::ERR_CONNECTION_REFUSED | no | Blocky block page |
| nos.nl | yes (http://nos.nl/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| nu.nl | yes (http://nu.nl/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| linkedin.com | yes (http://linkedin.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| manners.nl | yes (http://manners.nl/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| chess.com | yes (http://chess.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| temu.com | yes (http://temu.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| hardverapro.hu | yes (http://hardverapro.hu/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| reddit.com | yes (https://reddit.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |
| x.com | yes (http://x.com/) | net::ERR_CONNECTION_REFUSED | no (only Blocky's own extension worker is listed) | Blocky block page |

Answer: 1 of 10 domains fails in the normal profile and reaches Blocky's page in the fresh one (youtube.com).
