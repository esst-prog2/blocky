# Manual P1 results

Steps and pass/fail rules are in checklist.md.

| # | Check | Result | What it means |
|---|---|---|---|
| 1 | App closed mid-window | FAIL (gap) | Window set to end at 17:58. Entries present at 17:54:25; Blocky closed with the X button. At 18:18:28, 20 minutes after the end with no Python process running, all 10 entries were still in the hosts file and reddit.com resolved to 127.0.0.1 (wikipedia.org resolved normally). In Brave, a new reddit.com tab showed Brave's own "Deze site is niet bereikbaar" page (ERR_CONNECTION_REFUSED). Closing Blocky leaves its entries in place, so sites stay blocked after the window ends until Blocky is started again. Step 6: after Blocky was started again (outside the window), at 18:22:26 the hosts file had no Blocky entries and reddit.com resolved to its real addresses, so a restart cleans up. |
| 2 | Reboot with Blocky off | | |
| 3 | Declined UAC | FAIL (gap) | Clicking No on the UAC prompt, with both `pythonw -m blocky` and `python -m blocky`, shows nothing: no window and no message, and the console prints nothing. The user is not told that Blocky needs admin rights. Clicking Yes starts the app normally. The hosts file was not compared line by line; the Blocky entries from before were still there afterwards. |
| 4 | Brave idle 30+ min | PASS | reddit.com open in a normal tab; Brave minimised and untouched from before 18:24. Window started 18:58; entries appeared at 18:58:05. At 19:01, without clicking in it, the tab showed Blocky's page ("www.reddit.com is blocked until 20:00"). The one-minute sweep still redirects open tabs after Brave has been idle for over 30 minutes. |
| 5 | Firefox secure DNS | PASS | At both Max Protection (Custom, Cloudflare, "always warn" ticked) and Increased Protection (box unticked), reddit.com, chess.com, nos.nl, x.com and youtube.com showed Firefox's "Kan geen verbinding maken" page, and wikipedia.org loaded. Firefox with secure DNS does not get past Blocky's hosts entries. |
