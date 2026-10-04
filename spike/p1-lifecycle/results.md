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
| 6: Windows restarted with Blocky open | to do |
| 7b: Blocky ended in Task Manager, then started again | to do |
| 8: window ends during sleep (three cycles) | to do |
| 9c: Docker Desktop restarted during a window | to do |
