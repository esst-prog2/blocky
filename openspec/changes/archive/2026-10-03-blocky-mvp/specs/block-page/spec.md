## Purpose

Serves the friendly page that a blocked site redirects to, showing the shared suggestion shortlist, so that a block gives the user a useful alternative instead of a dead end.

## ADDED Requirements

### Requirement: Local server serves the block page while the app runs
The system SHALL run a local HTTP server, reachable only from this machine, that serves the block page while the app is running.

#### Scenario: Page available while app runs
- **WHEN** the app is running and a request arrives for the block page
- **THEN** the server responds with the block page

#### Scenario: Page unavailable when app is closed
- **WHEN** the app is closed
- **THEN** the block page is not served

### Requirement: Block page names the blocked domain and window end
The system SHALL show the blocked domain and the time the current block window ends on the block page.

#### Scenario: Block page content
- **WHEN** `reddit.com` is blocked until 17:00
- **THEN** the block page reads "reddit.com is blocked until 17:00"

### Requirement: Shortlist is defined once in the app
The system SHALL store one shared suggestion shortlist in the app and SHALL show that same shortlist on the block page and on the extension's new-tab page.

#### Scenario: Edited shortlist appears on the block page
- **WHEN** the user edits the shortlist in the app
- **THEN** the block page shows the edited shortlist on its next load

### Requirement: Shortlist is shown as a list
The system SHALL show the full shortlist on the block page.

#### Scenario: Multiple suggestions shown
- **WHEN** the shortlist contains "read tomorrow's lecture notes" and "10-minute walk"
- **THEN** the block page shows both suggestions
