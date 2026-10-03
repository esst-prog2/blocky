# Automated P1 results

Automated tests in tests/test_p1.py. Pass = behaviour as expected; fail = gap.

| Case | Result | What it means |
|---|---|---|
| Clock jumps forward past the window end | PASS | The entries are removed on the next check after the clock moves past the window's end. |
| Clock jumps backwards inside the window | PASS | The entries come back on the next check. |
| Port 8765 already in use | FAIL (gap) | The block-page server cannot start. The startup code stops there, so the process exits, and the background check stops with it. The entries already in the hosts file stay, but nothing updates them. The test records this behaviour deliberately; it is marked as a failure on purpose. |
| Background hosts-file failure shown to the user | FAIL (gap) | When the background check cannot write the hosts file, the error is kept in memory and never shown in the app's status. The user has no sign that blocking has stopped. |

Gaps: 2 of 4. Both are in the code. The port gap needs the server to fail without stopping blocking, and the failure to show in the app's status.
