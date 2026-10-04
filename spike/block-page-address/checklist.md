# Block page address check

Question: can the block page live at `blocky.localhost/<domain>` in Brave, instead of `http://127.0.0.1:8765/blocked?domain=<domain>`?

Setup: the agent runs `spike/block-page-address/serve.py`, a mock block page on port 80 (and on 8766 as the fallback), plus a start page.

In a normal Brave tab:

| # | Do this | Note what you see |
|---|---|---|
| 1 | Open `http://blocky.localhost/reddit.com` | Does the mock page load? What does the address bar show? Any "Not secure" label? |
| 2 | Look at the tab | Is the Blocky icon shown in the tab? |
| 3 | Open `http://127.0.0.1:8767/` and click the link | Does the mock page load? |
| 4 | On the same start page, press "Redirect by script" | Does the mock page load? (This is how the extension sends a tab.) |
| 5 | On the start page, click "Link to the fallback port 8766" | Does it load, and what does the address bar show? |

The agent also reads `requests.log` to see what Brave asked for, and whether it tried HTTPS on port 443.

Pass: 1 to 5 all load, the address bar shows `blocky.localhost/reddit.com` (5: with `:8766`) without a "Not secure" label, the icon shows, and Brave never tries HTTPS. Fail: any of these does not hold.
