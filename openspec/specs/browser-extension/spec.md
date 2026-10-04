# browser-extension Specification

## Purpose
Connects Brave to Blocky, so that a blocked site sends the user to the block page with the shortlist, without the user needing to remember to open the app.

## Requirements

### Requirement: Navigation to a blocked domain redirects to the block page
The extension SHALL redirect a tab to the app's block page when a navigation to a blocked domain, or to any subdomain of a blocked domain, starts during an active block window, before the request is made. It SHALL also redirect a tab when the page changes inside a blocked domain or one of its subdomains during an active block window, and when a block window starts while a tab is already open on a blocked domain or one of its subdomains. A subdomain is any hostname that ends with a dot followed by the blocked domain; a hostname that only ends with the same letters is not a subdomain.

#### Scenario: Blocked site redirected
- **WHEN** the user navigates to `reddit.com` during an active block window
- **THEN** the tab shows the block page instead of loading the site

#### Scenario: Site with a service worker is still redirected
- **WHEN** the user navigates to `youtube.com` during an active block window
- **THEN** the tab shows the block page instead of YouTube's own offline page

#### Scenario: Ordinary failure not redirected
- **WHEN** the user navigates to a domain that is not on the block list and the connection fails
- **THEN** the tab shows the browser's normal error page

#### Scenario: In-page navigation redirected
- **WHEN** the user moves between pages inside an open `reddit.com` tab during an active block window
- **THEN** the tab shows the block page instead of the new page

#### Scenario: Open tab redirected when a window starts
- **WHEN** a block window starts while a `reddit.com` tab is already open
- **THEN** that tab shows the block page within about a minute

#### Scenario: Subdomain redirected
- **WHEN** the user navigates to `old.reddit.com` or `music.youtube.com` during an active block window in which `reddit.com` and `youtube.com` are blocked
- **THEN** the tab shows the block page instead of loading the site

#### Scenario: Open subdomain tab redirected when a window starts
- **WHEN** a block window starts while a `music.youtube.com` tab is already open and `youtube.com` is blocked
- **THEN** that tab shows the block page within about a minute

#### Scenario: Lookalike domain not redirected
- **WHEN** `x.com` is blocked and the user navigates to `netflix.com` during an active block window
- **THEN** the site loads normally

#### Scenario: Subdomain of an overridden domain not redirected
- **WHEN** `reddit.com` has an active override and the user navigates to `old.reddit.com` during the block window
- **THEN** the site loads normally

### Requirement: Extension reads block list and shortlist from the app
The extension SHALL obtain the block list and shortlist from the app's local server and SHALL NOT keep its own editable copy.

#### Scenario: Change in app reaches extension
- **WHEN** the user adds a domain to the block list in the app
- **THEN** the extension treats that domain as blocked on its next check

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
