## Why

When the background check fails to update the hosts file, for example because Windows or antivirus briefly holds the file, it waits the full minute before trying again. A brief lock just after Blocky starts therefore delays blocking by a minute. The startup test, which waits 5 seconds for the first entries, failed this way twice on GitHub's Windows runner (most likely cause; the error itself was not captured).

## What Changes

- After a failed check, the background check tries again after 5 seconds instead of a minute; after a successful check it keeps the one-minute rhythm.
- A failure that keeps repeating is still logged once in errors.log and shown once as a warning.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `hosts-blocking`: the background-check requirement gains a retry after a failed update.

## Impact

- `blocky/checker.py`: `Checker.run` waits `RETRY_INTERVAL` (5 seconds) after a failure.
- `tests/test_checker.py`: a test that a failed first check is retried within seconds.
