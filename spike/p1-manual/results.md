# Manual P1 results

Steps and pass/fail rules are in checklist.md.

| # | Check | Result | What it means |
|---|---|---|---|
| 1 | App closed mid-window | | |
| 2 | Reboot with Blocky off | | |
| 3 | Declined UAC | FAIL (gap) | Clicking No on the UAC prompt, with both `pythonw -m blocky` and `python -m blocky`, shows nothing: no window and no message, and the console prints nothing. The user is not told that Blocky needs admin rights. Clicking Yes starts the app normally. The hosts file was not compared line by line; the Blocky entries from before were still there afterwards. |
| 4 | Brave idle 30+ min | | |
| 5 | Firefox secure DNS | PASS | At both Max Protection (Custom, Cloudflare, "always warn" ticked) and Increased Protection (box unticked), reddit.com, chess.com, nos.nl, x.com and youtube.com showed Firefox's "Kan geen verbinding maken" page, and wikipedia.org loaded. Firefox with secure DNS does not get past Blocky's hosts entries. |
