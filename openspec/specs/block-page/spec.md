# block-page Specification

## Purpose
Serves the friendly page that a blocked site redirects to, showing the shared suggestion shortlist, so that a block gives the user a useful alternative instead of a dead end.

## Requirements

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
The system SHALL store one shared suggestion shortlist in the app and SHALL show that shortlist on the block page.

#### Scenario: Edited shortlist appears on the block page
- **WHEN** the user edits the shortlist in the app
- **THEN** the block page shows the edited shortlist on its next load

### Requirement: Shortlist is shown as a list
The system SHALL show the full shortlist on the block page.

#### Scenario: Multiple suggestions shown
- **WHEN** the shortlist contains "read tomorrow's lecture notes" and "10-minute walk"
- **THEN** the block page shows both suggestions

### Requirement: Suggestions are added and changed one at a time
The system SHALL let the user add one suggestion at a time through an add box that accepts only 1 to 120 characters that are not already on the list, ignoring case, and SHALL list the suggestions as rows that can each be edited, saved and removed. Add and Save SHALL only be available when the text is valid.

#### Scenario: Suggestion added
- **WHEN** the user types "10-minute walk" and presses Add
- **THEN** "10-minute walk" is added to the end of the shortlist

#### Scenario: Duplicate suggestion
- **WHEN** the shortlist contains "10-minute walk" and the user types "10-Minute Walk"
- **THEN** Add is disabled and the hint says it is already in the list

#### Scenario: Suggestion edited
- **WHEN** the user changes "Tidy desk" to "Tidy the desk" and saves
- **THEN** the shortlist holds "Tidy the desk" in the same place
