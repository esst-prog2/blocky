# Review reruns (2026-10-05)

Two reruns asked for in the review of 2026-10-04, done in one sitting. Both need Blocky's own extension **turned off**, so nothing redirects and only the hosts file blocks. Turn it back on at the end.

**Domains (the HW4 ten):** nos.nl, nu.nl, reddit.com, x.com, youtube.com, chess.com, manners.nl, temu.com, hardverapro.hu, linkedin.com. **Control:** a name that does not exist, `nonexistent-test-blocky.example`, and a site that is not blocked, wikipedia.org.

## Setup

1. Make sure all ten domains are on Blocky's block list (manners.nl, temu.com, hardverapro.hu and linkedin.com may need adding for now; remove them afterwards if you like).
2. In Blocky, make a window that ends at least 45 minutes from now. Check with the helper that the entries are there:
   `powershell -ExecutionPolicy Bypass -File spike\p1-lifecycle\watch-hosts.ps1`
3. In Brave, open `brave://extensions`. Turn **Blocky off** (the switch on its card).
4. Turn on **Developer mode** (top right), click **Load unpacked**, and choose the folder `spike\console-logger` in the project.
5. On the new card "Blocky spike console logger", click **service worker** (next to "Inspect views"). A DevTools window opens; select its **Console** tab and press the clear button (the circle with a line through it).

## A. Console lines (spike hw4-console)

Keep Brave's secure DNS as it normally is for this part.

1. In a new tab, open `http://nonexistent-test-blocky.example/`.
2. Then open each of the ten domains in turn (type the name and press Enter, in the same tab is fine), for example `reddit.com`.
3. In the logger's console, right-click and choose **Save as...**, or select all lines and copy them. Paste them over the contents of `spike\console-normal.txt` and save.

**Note for each domain:** the page you saw (Brave's error page, or for youtube.com possibly YouTube's own offline page).

## B. Secure DNS without the extension (spike secure-dns-no-extension)

1. Open `brave://settings/security`. Under **Use secure DNS**, choose **With Cloudflare (1.1.1.1)**.
2. Press Ctrl+Shift+Delete and clear **Cached images and files** for "Last hour", so no page comes from the cache.
3. Open each of the ten domains. For each, note: **real site** (the site loads) or **blocked** (Brave's "can't connect" page, or the site's own offline page). Then open wikipedia.org; it should load.
4. Turn secure DNS **off** (the switch above the choice), clear the cache again as in step 2, and do step 3 again.

**Pass:** in both settings none of the ten loads the real site, and wikipedia.org loads.

## Afterwards

1. In `brave://extensions`, remove the logger (Remove on its card) and turn **Blocky on** again.
2. Put secure DNS back the way you had it.
3. Send me the notes from A and B, and save `spike\console-normal.txt`.
