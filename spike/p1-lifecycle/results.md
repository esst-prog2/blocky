# Spike p1-lifecycle results

Question: does Blocky behave as expected in P1 cases 6 to 9 (Windows shut down or restarted with Blocky open, Blocky force-closed, a window ending during sleep, Docker Desktop editing the hosts file)?

## Automated (tests/test_p1_lifecycle.py, 2026-10-04)

| Check | Result |
|---|---|
| 9a: Docker's lines while Blocky blocks and unblocks | **Pass.** Docker's block stays byte-for-byte the same, and unblocking gives back the original file. |
| 9b: a Docker change made while Blocky is between reading and writing the hosts file | **Fail (gap).** Blocky writes back the file as it read it, so Docker's new address (10.67.80.2 in the test) is replaced by the old one (10.67.73.13). The test is marked as a known failure until this is decided. |
| 7a: background check killed mid-window, then a new start after the window ended | **Pass.** After the kill the entries stay (expected); the first check of the new start removes them and leaves the rest of the file exactly as it was, with no hosts.tmp left. |

On 9b: the gap needs Docker to write within the few milliseconds between Blocky's read and its write. Docker writes the hosts file when it starts and when its network address changes; Blocky writes when it starts, when a window starts or ends, and after a change in the window. If it happens, `host.docker.internal` keeps the old address until Docker writes again.

## Manual (spike/p1-lifecycle/checklist.md)

| Check | Result |
|---|---|
| 6: Windows restarted with Blocky open | **Fail (gap).** Window until 19:30, Blocky open, Windows restarted; no message at shutdown or login. At 19:18:37, Blocky not started, all 14 Blocky entries were still there (and Docker's 3 lines). Windows ended Blocky without its close cleanup, so the entries stay until Blocky starts again, also after the window ends. |
| 7b: Blocky ended in Task Manager, then started again | **Pass.** Window set to end 19:27; Blocky ended at 19:25. At 19:29:53 all 14 entries were still there (expected). Blocky started again at about 19:30; the first watch line at 19:30:31 showed 0 entries, so within about 30 s. Docker's 3 lines stayed. |
| 8: window ends during sleep (three cycles) | **Pass.** Cycle 1: ended 19:36, asleep 19:33; after waking 14 entries at 19:39:09, 0 at 19:39:19. Cycle 2: ended 19:45, asleep 19:42, block page seen before sleep; woken 19:47, 0 entries at the first reading 19:47:23. Cycle 3: ended 19:50, asleep 19:48; 14 entries at 19:52:28, 0 at 19:52:38. All within 60 s of waking. Docker's 3 lines stayed. |
| 9c: Docker Desktop restarted during a window | **Pass.** Run by the agent with `docker desktop restart` at 20:02:14, window until 20:30 (restarting from the Docker window only reconnected to the running engine). Docker was running again at 20:02:41; for 60 s after, the 14 Blocky entries and Docker's 3 lines stayed, addresses unchanged (10.67.73.13). The hosts file was last written at 19:56:04 throughout: Docker did not rewrite its lines on this restart, since its address stayed the same, so a real Docker write next to Blocky is covered only by 9a and 9b. |

## Answer

5 of 7 checks pass (9a, 7a, 7b, 8, 9c). Two gaps:

- **6:** when Windows restarts or shuts down with Blocky open, Blocky's close cleanup does not run and no message is shown, so the entries stay, also after the window ends, until Blocky starts again (it then cleans up, as 7a and 7b show).
- **9b:** a Docker write that falls between Blocky reading and writing the hosts file is overwritten with Docker's old lines. Rare: on the real restart (9c) Docker did not write at all.

Blocky ended by force (7) leaves its entries until it starts again, and then removes them within about 30 seconds; that is the trade-off accepted for case 2. A window that ends during sleep (8) is cleared within about 10 to 25 seconds of waking.
