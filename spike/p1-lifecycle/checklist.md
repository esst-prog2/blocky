# P1 lifecycle checks (cases 6 to 9)

Four checks that need the real machine. For each one, write down the times and what you saw, and paste them back.

**Helper:** `powershell -ExecutionPolicy Bypass -File spike\p1-lifecycle\watch-hosts.ps1` prints the time, the number of Blocky entries and Docker's lines in the hosts file, with the lines themselves. Add `-Watch` to print the counts every 10 seconds until you press Ctrl+C. Reading the hosts file does not need admin rights.

**Test site:** reddit.com (on the block list). Start Blocky from its shortcut as usual.

**A window ending soon:** in Blocky's Schedule tab, tick today and set the end a few minutes from now, with a start before now; press Save schedule.

---

## 6. Windows shut down or restarted with Blocky open

Does Blocky remove its entries when Windows restarts while it is open?

1. Make a window that ends at least 15 minutes from now. Wait until reddit.com shows the block page.
2. Run the helper: Blocky entries should be there. Note the time.
3. With Blocky still open, restart Windows (Start, Power, Restart). Note anything Windows shows, such as "Blocky is preventing Windows from restarting" or "pythonw".
4. After logging in, do **not** start Blocky. Run the helper.

**Pass:** at step 4 there are no Blocky entries.
**Fail (gap):** at step 4 the Blocky entries are still there.
**Also record:** whether Windows showed a message at step 3, and whether you had to press anything.

## 7b. Blocky ended in Task Manager

Does starting Blocky again clean up after it was ended by force?

1. Make a window that ends 4 minutes from now. Wait until reddit.com shows the block page.
2. Open Task Manager, Details tab. Find `pythonw.exe` (Blocky; the one with "Blocky" in the command line if there are several: right-click a column header, Select columns, Command line). Right-click it and choose End task. Note the time.
3. Wait until 2 minutes after the window's end time. Run the helper (entries are expected to still be there).
4. Start Blocky. Right away run the helper with `-Watch` and leave it for 70 seconds.

**Pass:** the Blocky entries are gone within 60 seconds of starting Blocky at step 4.
**Fail (gap):** they are still there after 60 seconds.
**Also record:** whether the entries were still there at step 3 (expected: yes).

## 8. Window ends during sleep

How soon after waking are the entries gone when the window ended during sleep? Do this three times.

1. Make a window that ends 4 minutes from now. Wait until reddit.com shows the block page. Leave Blocky open.
2. Before the end time, put the PC to sleep (Start, Power, Sleep). Note the time.
3. Wake it at least 2 minutes after the end time. Log in and right away run the helper with `-Watch`. Note the wake time (the first line's time is close enough).
4. Stop the helper once the count shows 0 Blocky entries, or after 2 minutes.

**Pass:** in all three cycles the Blocky entries are gone within 60 seconds of waking.
**Fail (gap):** in any cycle they are still there 60 seconds after waking.
**Also record:** for each cycle, the seconds from waking until 0 entries.

## 9c. Docker Desktop rewrites its lines while Blocky is open

Do Blocky's entries and Docker's lines both survive a Docker Desktop restart?

1. Make sure Docker Desktop is running. Make a window that ends at least 10 minutes from now. Wait until reddit.com shows the block page.
2. Run the helper: note the Blocky entries and the Docker lines (with their addresses).
3. Restart Docker Desktop (whale icon in the tray, Restart; or quit it and start it again). Right away run the helper with `-Watch`.
4. When Docker Desktop shows it is running again, wait 60 seconds more, stop the watch and run the helper once without `-Watch`.

**Pass:** at step 4 the Blocky entries and Docker's lines are both there.
**Fail (gap):** either is missing, or Docker's lines are back but with the address from before the restart while Docker shows another one.
**Also record:** whether Docker's addresses changed between step 2 and step 4.
