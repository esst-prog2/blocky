# Robustness results

Automated tests in tests/test_robustness.py. Pass = behaviour as expected; fail = gap.

| Case | Result | What it means |
|---|---|---|
| Checker keeps running after an unexpected error | FAIL | After one unexpected error the background check stops, with no message. Blocking would stop silently. |
| Hosts reset by another program is restored by the next sync | PASS | Blocky puts its entries back on the next check. |
| Failed hosts write leaves the original file intact | FAIL | If the write fails partway, the hosts file is left cut short, which can break internet access on this PC. |
| Window logic across the daylight-saving change | PASS | The window follows wall-clock time, including the repeated hour. |
| Override survives a restart | PASS | An override still applies after reopening, and expires at the window's end. |
| Removed domain leaves the hosts file mid-window | PASS | Removing a domain removes its entry at once. |

Gaps: 2 of 6. Both are in the code, not in the design, and both have simple fixes (catch all errors in the checker and keep looping; write the hosts file to a temporary file, then replace it).
