# VPN results (Surfshark)

Blocking active, the five domains blocked, a window active. Each domain typed with https:// in front.

| Domain | Surfshark off | Surfshark on |
|---|---|---|
| reddit.com | Blocky's block page | Blocky's block page |
| x.com | Blocky's block page | Blocky's block page |
| nos.nl | Blocky's block page | Blocky's block page |
| chess.com | Blocky's block page | Blocky's block page |
| youtube.com | Blocky's block page | Blocky's block page |

Real sites loaded with Surfshark on: 0 of 5.

Caveat: Blocky's page is shown by the Brave extension, which redirects before the request is made, so this run does not show whether the VPN bypasses the hosts file. A private window (no extension) with Surfshark on would show that.

## Private window with Surfshark on

Brave private window (no extension), Surfshark on, blocking active. Each domain typed with https:// in front.

| Domain | Result |
|---|---|
| reddit.com | Browser's error page (ERR_CONNECTION_REFUSED) |
| x.com | Browser's error page (ERR_CONNECTION_REFUSED) |
| nos.nl | Browser's error page (ERR_CONNECTION_REFUSED) |
| chess.com | Browser's error page (ERR_CONNECTION_REFUSED) |
| youtube.com | Browser's error page (ERR_CONNECTION_REFUSED) |

Real sites loaded with Surfshark on, in a private window: 0 of 5. The VPN did not get past the hosts-file block in this test. This covers one Surfshark connection.
