## 1. Spikes (verify assumptions before building)

- [ ] 1.1 Confirm the app can run elevated and write the hosts file without a UAC prompt in customtkinter; record the result in design.md
- [ ] 1.2 Confirm in Brave that a failed navigation to a blocked domain fires an event the extension can see, for `reddit.com`, `youtube.com`, and `x.com`; record the result in design.md
- [ ] 1.3 Confirm in Brave that an extension's new-tab page override replaces the default new tab; record the result in design.md

## 2. Project setup

- [x] 2.1 Create the Python project structure and dependency file, and verify the app starts an empty window
- [x] 2.2 Create the YAML config file for block list, schedule, shortlist, and override log, and verify it loads with defaults when missing

## 3. Block list and schedule

- [x] 3.1 Implement domain validation and verify that `reddit`, `red dit.com`, and `reddit.com` produce the expected accept or reject results in unit tests
- [ ] 3.2 Implement add, edit, and remove for block-list entries in the UI, and verify the entries persist after restart
- [x] 3.3 Implement the `www.` variant expansion and verify that `youtube.com` yields both hostnames
- [x] 3.4 Implement the single weekly schedule (weekday set plus one time range) and verify the active-window function with unit tests for inside, outside, and edge times
- [ ] 3.5 Show the schedule as "Schedule" with no option to add another, and verify in the UI

## 4. Hosts-file blocking

- [x] 4.1 Implement reading and writing Blocky-marked entries in the hosts file, leaving other lines untouched, and verify with a test hosts file
- [x] 4.2 Implement the background check every minute that adds entries during active windows and removes them outside, and verify with a test clock
- [x] 4.3 Implement cleanup of leftover Blocky entries at startup, and verify with a test hosts file containing a stale entry
- [ ] 4.4 Verify the write succeeds on the real hosts file with the app elevated and no UAC prompt during a session

## 5. Override and history

- [x] 5.1 Implement override for a currently blocked domain requiring a non-empty reason, and verify an empty reason is rejected
- [x] 5.2 Implement the override lasting until the current window ends, and verify with a test clock that the domain re-blocks at the next window start
- [x] 5.3 Log each override with domain, timestamp, and reason, and verify the log entry is written
- [ ] 5.4 Implement the History tab listing overrides, and verify it shows an empty list with no history

## 6. Status panel

- [x] 6.1 Implement the status panel showing blocked domains and time remaining, and verify the "Blocking active — 3h 00m remaining" text with a test clock
- [ ] 6.2 Show overridden domains with "unblocked until" and a countdown, and verify in the UI
- [ ] 6.3 Update the panel at least once per minute, and verify the countdown advances while the app is open

## 7. Block page and shortlist

- [x] 7.1 Implement the local HTTP server bound to 127.0.0.1 that serves the block page while the app runs, and verify it responds only from localhost and stops when the app closes
- [x] 7.2 Render the blocked domain and window end on the block page, and verify the text matches the domain and time
- [ ] 7.3 Implement the shared shortlist editable in the app and rendered as a list on the block page, and verify edits appear on the next page load

## 8. Brave extension

- [ ] 8.1 Create the Manifest V3 extension with a new-tab override that shows the shortlist from the app's local server, and verify in `brave://extensions` after loading unpacked
- [ ] 8.2 Implement the redirect on failed navigation to a blocked domain during an active window, and verify `reddit.com` shows the block page
- [ ] 8.3 Verify an ordinary failed navigation to a non-blocked domain still shows Brave's error page
- [ ] 8.4 Verify the extension reads the block list and shortlist from the app and keeps no editable copy of its own

## 9. End-to-end check

- [ ] 9.1 Walk through the README demo in Brave: block active, reddit.com redirected to the block page, override with reason, status panel updated, override shown in History
- [ ] 9.2 Verify each criterion in README section 4 with the app running and record the results in the change folder
