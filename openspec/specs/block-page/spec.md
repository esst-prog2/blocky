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

### Requirement: Block page has a readable address
The system SHALL serve the block page at `http://blocky.localhost/<domain>`, without a port number when port 80 on this machine is free, and at `http://blocky.localhost:8765/<domain>` when it is not. The server SHALL only accept connections from this machine on both ports. A request for the earlier address `/blocked?domain=<domain>` SHALL be sent on to the new address.

#### Scenario: Port 80 free
- **WHEN** `reddit.com` is blocked, port 80 is free when Blocky starts, and the user opens reddit.com in Brave
- **THEN** the address bar shows `blocky.localhost/reddit.com`

#### Scenario: Port 80 taken
- **WHEN** another program uses port 80 when Blocky starts and the user opens a blocked site in Brave
- **THEN** the block page opens at `blocky.localhost:8765/<domain>`

#### Scenario: Earlier address
- **WHEN** a browser asks for `/blocked?domain=reddit.com`
- **THEN** it is sent on to `blocky.localhost/reddit.com` (or the port 8765 address when port 80 is taken)

### Requirement: Block page follows the appearance settings
The system SHALL show the block page in the colours of the theme the window currently uses, in the chosen font and at the chosen text size, and SHALL give the page's browser tab the icon of that theme. The page SHALL show the theme's icon next to the name Blocky, and SHALL make the blocked domain and the end time stand out from the rest of the sentence, without a countdown. A change of setting SHALL show on the next load of the block page.

#### Scenario: Light theme on the block page
- **WHEN** the window uses the Aqua theme with Georgia at Large and the user opens a blocked site
- **THEN** the block page uses the Aqua colours, Georgia at 115 percent, and the Aqua icon in its tab

#### Scenario: Domain and end time stand out
- **WHEN** `reddit.com` is blocked until 17:00 in any theme
- **THEN** the page shows the theme's icon next to Blocky, and "reddit.com" and "17:00" are emphasised in the sentence "reddit.com is blocked until 17:00", with no countdown

#### Scenario: Theme changed while the block page is open
- **WHEN** the user changes the theme while a block page is open in Brave and then reloads that page
- **THEN** the reloaded page shows the new theme
