# Subdomain results

Window active until 21:00; reddit.com, youtube.com and x.com blocked. Each address opened in a new normal Brave tab. "Resolves to" was checked by the agent at the same time.

| Address | Resolves to | What Brave showed |
|---|---|---|
| old.reddit.com | 199.232.17.140 (real) | The real site (old Reddit's login page) |
| new.reddit.com | 199.232.17.140 (real) | Blocky's page for www.reddit.com: Reddit itself redirected to www.reddit.com, which is blocked |
| m.youtube.com | 142.250.120.100 (real) | Blocky's page for www.youtube.com: YouTube redirected to www.youtube.com |
| music.youtube.com | 142.250.130.91 (real) | The real site (YouTube Music) |
| mobile.x.com | 172.66.0.227 (real) | Blocky's page for x.com: X redirected to x.com |

Result: FAIL (gap). None of the subdomains are blocked by Blocky. Three ended on Blocky's page only because the site itself redirected to the main domain; old.reddit.com and music.youtube.com loaded. Cause: Blocky writes only the domain and its www. variant to the hosts file, and the extension only redirects exact matches.
