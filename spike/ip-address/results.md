# IP address results

Blocking active, all five domains in the block list. Each address was tried as http:// and https://.
The real site counts as loaded only if the site itself appears. Screenshots are named screenshot-29.png to screenshot-37.png.

| Site | Address | http:// result | https:// result | Real site loaded? |
|---|---|---|---|---|
| reddit.com | 151.101.65.140 | Fastly "unknown domain" error | Certificate mismatch error | No |
| x.com | 162.159.140.229 | "error code: 1003" | SSL version or cipher mismatch | No |
| youtube.com | 142.250.109.91 | Google homepage (google.com) | Google homepage (google.com) | No (a different site, Google, loaded) |
| nos.nl | 13.32.12.24 | CloudFront 403 error | SSL version or cipher mismatch | No |
| chess.com | 104.18.137.67 | "error code: 1003" | Cloudflare 403 Forbidden | No |

Count of the five real sites loaded by IP address: 0 of 5.
