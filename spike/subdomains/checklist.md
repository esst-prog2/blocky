# Subdomain check

Question: during an active window, are subdomains of blocked sites blocked?

Setup: Blocky running, window active (reddit.com shows the block page in Brave).

Open each address in a new normal Brave tab and note what you see:

| Address | Blocky's page / browser error / site loads |
|---|---|
| old.reddit.com | |
| new.reddit.com | |
| m.youtube.com | |
| music.youtube.com | |
| mobile.x.com | |

The agent also checks what each address resolves to (127.0.0.1 = blocked by the hosts file).

Pass: none of them load the real site. Fail (gap): any of them loads.
