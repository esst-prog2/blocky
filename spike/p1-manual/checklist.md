# P1 manual checks

Five checks that need the real machine. For each one, write down the times and what you saw, and paste them back.

**Helper:** `powershell -ExecutionPolicy Bypass -File spike\p1-manual\show-hosts.ps1` prints the time and Blocky's entries in the hosts file. Reading the hosts file does not need admin rights.

**Test site:** reddit.com (on the block list). **Control site:** wikipedia.org (not on the list).

**Ctrl+Shift+R** in Brave and Firefox reloads without the browser cache. Windows also caches DNS: if a result looks wrong, run `ipconfig /flushdns` and try again, and say that you did.

---

## 1. App closed mid-window

Are sites still blocked after the window ends if Blocky was closed during it?

1. In Blocky, set the schedule to today, ending 3 minutes from now. Wait until reddit.com shows the block page.
2. Run the helper: entries should be there. Note the time.
3. Close Blocky with the window's X button.
4. Wait until 2 minutes after the window's end time.
5. Run the helper. Open reddit.com in Brave.
6. Start Blocky again. Wait 60 seconds and run the helper again.

**Pass:** at step 5 there are no entries, and reddit.com loads.
**Fail (gap):** at step 5 the entries are still there, or reddit.com is blocked.
**Also record:** whether step 6 cleans up the entries.

## 2. Reboot with Blocky off

Do leftover entries still block after a reboot?

1. Set the schedule to end 5 minutes from now. Wait until reddit.com is blocked.
2. Close Blocky. Run the helper and note the time.
3. Restart Windows. Do **not** start Blocky after logging in.
4. After the window's end time, run the helper. Open reddit.com in Brave.

**Pass:** no entries, and reddit.com loads.
**Fail (gap):** the entries are still there, or reddit.com is blocked.

## 3. Declined UAC prompt

What happens if you click "No" on the admin prompt?

1. Close Blocky. Run the helper and note what it shows.
2. Run `pythonw -m blocky` and click **No** on the UAC prompt.
3. Wait 10 seconds. Note anything you see (a window, a message, nothing).
4. Run the helper again.
5. Repeat with `python -m blocky` in a console, and copy anything the console prints.

**Pass:** you are told that Blocky needs admin rights, and the hosts file has not changed.
**Fail (gap):** nothing happens, with no message.

## 4. Brave idle for 30+ minutes

Does the one-minute sweep still redirect an open tab after Brave has been idle for a long time?

1. Blocky running, outside a window. Open reddit.com in a normal Brave tab.
2. Set the schedule to start 35 minutes from now.
3. Leave Brave alone for the whole time: no clicks or typing in Brave. Minimise it. Leave the PC awake (no sleep).
4. Without touching Brave, run the helper every couple of minutes after the start time, and note when the entries appear.
5. Then, still without clicking in the reddit tab, look at it. Note the time the block page appeared, if you can tell. Otherwise note whether it is showing the block page when you look.

**Pass:** the reddit tab shows the block page within about 60 seconds of the entries appearing.
**Fail (gap):** the tab still shows reddit until you interact with it.

## 5. Firefox secure DNS

Do blocked sites load in Firefox with secure DNS on?

1. Blocky running, inside a window (reddit.com blocked in Brave).
2. In Firefox, go to Settings → Privacy & Security → DNS over HTTPS and select **Increased Protection** (Cloudflare).
3. Open reddit.com, youtube.com and x.com. Reload each with Ctrl+Shift+R. Also open wikipedia.org.
4. Switch to **Max Protection** and repeat step 3.
5. Put the setting back to what it was before.

**Pass:** at both levels, none of the blocked sites load (any error page counts), and wikipedia.org loads.
**Fail (gap):** any blocked site loads its real content.

---

## Results

| # | Check | Result | Times / notes |
|---|---|---|---|
| 1 | App closed mid-window | | |
| 2 | Reboot with Blocky off | | |
| 3 | Declined UAC | | |
| 4 | Brave idle 30+ min | | |
| 5 | Firefox secure DNS | | |
