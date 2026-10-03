# Automated P1 config results

Tests in tests/test_p1_config.py. Pass = behaviour as expected; fail = gap.

| Case | Result | What happens now |
|---|---|---|
| 10. Config save hits a brief lock (3 "access denied" on the swap) | FAIL (gap) | The save fails with PermissionError at once. config.yaml is swapped into place like the hosts file was, without the retries the hosts file now has. In the app this shows as a red error and the change is lost. |
| 11. Invalid YAML: window opens with a warning | FAIL (gap) | Reading the config raises ParserError while the window is built, so the window never opens. Under pythonw nothing is shown. |
| 11. Zero bytes (what a power cut can leave): window opens with a warning | FAIL (gap) | Same, with ReaderError. |
| 11. Empty file: window opens with a warning | FAIL (gap) | Loads as an empty block list without a word: nothing is blocked, and the next save overwrites the file. |
| 11. Domains written as text: window opens with a warning | FAIL (gap) | `domains: reddit.com` loads as the letters r, e, d, d, i, t; no warning. |
| 11. Invalid YAML / zero bytes / empty file: no wrong hosts entries | PASS | The background check fails or writes nothing wrong. |
| 11. Domains written as text: no wrong hosts entries | FAIL (gap) | The hosts file gets entries such as `127.0.0.1 r` and `127.0.0.1 www.r`. |

Gaps: 6 of 9. All in config.py: saving has no retry, and loading does not check that the file is a valid Blocky config. Invalid YAML and a zero-filled file stop Blocky from starting with no message.
