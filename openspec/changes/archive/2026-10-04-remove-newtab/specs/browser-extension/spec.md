## REMOVED Requirements

### Requirement: New tab shows the shortlist
**Reason**: Taking over every new tab assumes the user wants to be distracted from whatever they opened it for; the suggestions belong on the block page, when a blocked site was actually requested.
**Migration**: None needed; after reloading the extension, Brave shows its own new tab again.

## MODIFIED Requirements

### Requirement: Extension works in Brave loaded unpacked
The extension SHALL run in Brave when loaded unpacked in developer mode, without publishing to a web store.

#### Scenario: Loaded unpacked
- **WHEN** the user loads the extension folder in `brave://extensions` with developer mode on
- **THEN** the extension is active and a navigation to a blocked domain during an active block window opens the block page

### Requirement: Extension does not block on its own
The extension SHALL NOT decide which domains are blocked; the block list comes from the app, and the blocked domains and their `www.` variants are blocked by the hosts file written by the app. Subdomains of blocked domains SHALL be blocked by the extension only, so they are blocked in Brave windows where the extension runs and not elsewhere.

#### Scenario: Extension disabled
- **WHEN** the extension is disabled
- **THEN** blocked domains still fail to load, and only the redirect to the block page is lost

#### Scenario: Subdomain without the extension
- **WHEN** the extension is disabled, or another browser is used, during an active block window
- **THEN** subdomains of blocked domains, such as `old.reddit.com`, load normally
