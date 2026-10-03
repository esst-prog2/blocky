## Purpose

Connects Brave to Blocky, so that a blocked site sends the user to the block page and a new tab shows the shortlist, without the user needing to remember to open the app.

## ADDED Requirements

### Requirement: Navigation to a blocked domain redirects to the block page
The extension SHALL redirect a tab to the app's block page when a navigation to a blocked domain starts during an active block window, before the request is made.

#### Scenario: Blocked site redirected
- **WHEN** the user navigates to `reddit.com` during an active block window
- **THEN** the tab shows the block page instead of the browser's error page

#### Scenario: Ordinary failure not redirected
- **WHEN** the user navigates to a domain that is not on the block list and the connection fails
- **THEN** the tab shows the browser's normal error page

### Requirement: New tab shows the shortlist
The extension SHALL replace the new-tab page with the shortlist, served by the app.

#### Scenario: New tab opened
- **WHEN** the user opens a new tab in Brave
- **THEN** the tab shows the shortlist from the app

### Requirement: Extension reads block list and shortlist from the app
The extension SHALL obtain the block list and shortlist from the app's local server and SHALL NOT keep its own editable copy.

#### Scenario: Change in app reaches extension
- **WHEN** the user adds a domain to the block list in the app
- **THEN** the extension treats that domain as blocked on its next check

### Requirement: Extension works in Brave loaded unpacked
The extension SHALL run in Brave when loaded unpacked in developer mode, without publishing to a web store.

#### Scenario: Loaded unpacked
- **WHEN** the user loads the extension folder in `brave://extensions` with developer mode on
- **THEN** the extension is active and its new-tab page is the shortlist

### Requirement: Extension does not block on its own
The extension SHALL NOT decide what is blocked; blocking is performed only by the hosts file written by the app.

#### Scenario: Extension disabled
- **WHEN** the extension is disabled
- **THEN** blocked domains still fail to load, and only the redirect and new-tab page are lost
