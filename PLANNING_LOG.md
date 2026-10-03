2026-10-03 | Blocking uses the Windows hosts file and blocks whole domains | you decided
2026-10-03 | The MVP includes the custom block page and the suggestion shortlist | you decided
2026-10-03 | Plain-HTTP block page is not the trigger; a Brave extension replaces it | agent proposed, you decided
2026-10-03 | Extension replaces the new-tab page and redirects when a blocked site fails to load | agent proposed, you decided
2026-10-03 | Extension reads the block list and shortlist from a local server in the app | agent proposed, you decided
2026-10-03 | The app serves the blocked-site page, so it works only while the app runs | agent proposed, you decided
2026-10-03 | Browser is Brave (Chromium) | you decided
2026-10-03 | Entering a domain also blocks its www. variant | agent proposed, you decided
2026-10-03 | "Study Mode" is dropped; one schedule labeled "Schedule" | agent proposed, you decided
2026-10-03 | One time range applies to the chosen weekdays; per-day ranges are a later level | agent proposed, you decided
2026-10-03 | The app runs elevated from start, avoiding mid-session UAC prompts (to verify in a spike) | agent proposed, you decided
2026-10-03 | An override lasts until the current scheduled block window ends | agent proposed, you decided
2026-10-03 | Hosting the block page on a Raspberry Pi or in the cloud is a later level; blocking stays local | you decided
2026-10-03 | Tools: Python 3.11, customtkinter 6.0.0, PyYAML 6.0.2, pytest | agent proposed, you decided
2026-10-03 | Config and override history are stored in %APPDATA%\Blocky\config.yaml | agent proposed, you decided
2026-10-03 | Hosts entries are written only between "# BEGIN BLOCKY" and "# END BLOCKY" | agent proposed, you decided
2026-10-03 | Local server uses fixed port 8765 on 127.0.0.1 with no CORS header; the extension will use host permissions | agent proposed, you decided
2026-10-03 | The app relaunches itself elevated at startup, which shows one UAC prompt (to verify in spike 1.1) | agent proposed, you decided
2026-10-03 | The extension requests webNavigation and all-URLs host access, needed to see failed navigations (to verify in spike 1.2) | agent proposed, you decided
2026-10-03 | On a failed navigation to a blocked domain, the extension asks the app for its state at that moment and redirects; it keeps no cache | agent proposed, you decided
2026-10-03 | The new tab redirects to the app's shortlist, and shows a "not running" message when the app is closed | agent proposed, you decided
2026-10-03 | Tests use pytest for Python and Node's built-in test runner for the extension logic | agent proposed, you decided
2026-10-03 | Spike 1.1 result: the elevated app wrote reddit.com and www.reddit.com to the hosts file during an active window with no UAC prompt after launch | observed by you
2026-10-03 | Spike 1.2 result: reddit.com and x.com redirected to the block page; youtube.com showed Brave's "no internet connection" page instead; ordinary failing sites showed Brave's error page | observed by you
2026-10-03 | youtube.com showing the browser's page instead of Blocky's is accepted as a limitation; it stays blocked | you decided
2026-10-03 | Spike 1.3 result: the new tab shows the shortlist when Blocky runs, and the "not running" message when it does not | observed by you
2026-10-03 | Styling the block page and the new tab is a later level | you decided
2026-10-03 | Step 7 results: schedule tab shows one "Schedule"; status countdown moves; README demo walks through except that an override cannot be undone; section 4 criteria a, b, c, e hold; criterion d holds for reddit.com and x.com but not youtube.com | observed by you
2026-10-03 | An override cannot be undone before its window ends; a decision on this is pending | observed by you
2026-10-03 | Undo button: re-blocks at once, keeps the override line in history and adds an "override undone" line | you decided
2026-10-03 | youtube.com shows YouTube's own connection page rather than Blocky's; accepted as a limitation, stated in README section 4 | you decided
2026-10-03 | Logic moved into a controller class so tests run without creating a window per test; the window is created once in a smoke test | agent proposed, you decided
2026-10-03 | Undo button verified in the app: re-blocks at once, history shows both the override and the undo line | observed by you
2026-10-03 | The "Your spike" issue is not in the repository; the owner has asked the teacher for it, and the spike has not started | observed by you
2026-10-03 | Blocky keeps the UAC prompt on each launch; no scheduled task with highest privileges | you decided
2026-10-03 | Blocky stays a desktop app with hosts-file blocking; a Chrome-only extension replacement is rejected because other browsers would be unblocked | you decided
2026-10-03 | HW4 spike question: of ten sites I would really block, how many fail to reach Blocky's page in my normal Brave profile but reach it in a fresh profile? | set by course spike issue
2026-10-03 | HW4 spike domains, fixed before testing: nos.nl, nu.nl, reddit.com, x.com, youtube.com, chess.com, manners.nl, temu.com, hardverapro.hu, linkedin.com | you decided
2026-10-03 | HW4 spike answer: a table per domain and profile (event fired, error string, service worker registered, page seen), then one number: how many of ten fail in the normal profile and reach the page in the fresh one. If zero, the limitation stands; if one or more, the listener changes | set by course spike issue
2026-10-03 | HW4 spike answer: 1 of 10 domains fail to reach Blocky's page in the normal profile but reach it in a fresh profile (youtube.com). In the normal profile youtube.com showed YouTube's own offline page, with no onErrorOccurred line; in the fresh profile it fired onErrorOccurred (net::ERR_CONNECTION_REFUSED) and showed Blocky's page, with no service worker registered. The remaining nine domains are being checked in the fresh profile for the table | observed by you
2026-10-03 | HW4 spike change: the extension listens for webNavigation.onBeforeNavigate on blocked hostnames and redirects then, instead of waiting for onErrorOccurred; the browser-extension spec's "connection fails" condition becomes "navigation starts" (to verify in Brave) | you decided
2026-10-03 | Task 1.2 closed: the failed-navigation event works for 9 of 10 tested domains; youtube.com is the accepted exception, per the HW4 spike | you decided
2026-10-03 | early-block-redirect check 2.1: reddit.com, x.com, nos.nl and chess.com (https://) show Blocky's block page with the early redirect | observed by you
2026-10-03 | early-block-redirect check 2.2 FAILED: youtube.com (https://) still shows YouTube's own offline page with the onBeforeNavigate listener | observed by you
2026-10-03 | early-block-redirect check 2.2 PASSED: youtube.com shows Blocky's block page on three visits after reloading the extension; debug logging removed | observed by you
2026-10-03 | early-block-redirect check 2.3 PASSED: an ordinary site (wikipedia.org) loads normally | observed by you
2026-10-03 | early-block-redirect check 2.4 PASSED: with Blocky closed, reddit.com shows the browser's normal error page | observed by you
2026-10-03 | Correction to the window-start-delay answer: the 46-second figure came from five runs that lined up with the same check time; a later run (override-end spike) took 5 seconds, so blocking starts between 0 and 60 seconds after a window opens. README updated to say so | agent proposed, you decided
2026-10-03 | Gap found: a reddit.com tab already open when a window starts keeps working for moving between pages, but a reload (F5) is blocked; the extension only redirects new navigations, so in-page navigation is not caught | observed by you
2026-10-03 | open-tab-block check 2.2 PASSED: a reddit.com tab that was open before the window started changed to Blocky's block page 46 seconds after 16:27 (16:27:46), while the owner was still on the site | observed by you
2026-10-03 | open-tab-block check 2.1 PASSED: clicking into a post in an open reddit.com tab immediately after a window started showed the block page straight away. This does not show whether the in-page listener or the one-minute sweep caught the move | observed by you
2026-10-03 | open-tab-block check 2.3 PASSED: wikipedia.org loads normally while reddit.com is blocked during an active window | observed by you
2026-10-03 | open-tab-block check 2.4 PASSED: reloading reddit.com during an active window still shows the block page | observed by you
2026-10-03 | Spike vpn-dns question: does a VPN (Brave's built-in VPN, if available) let a blocked site load past the hosts-file block? | you decided
2026-10-03 | Spike vpn-dns answer criteria: five blocked sites (reddit.com, x.com, nos.nl, chess.com, youtube.com) visited with blocking active, once with Brave's VPN on and once with it off; the answer is the count of sites where the real site loads with the VPN on, out of five, and the count of Blocky's page results; if Brave's VPN is not available, record that and use another VPN | you decided
