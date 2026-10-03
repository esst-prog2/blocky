## MODIFIED Requirements

### Requirement: Navigation to a blocked domain redirects to the block page
The extension SHALL redirect a tab to the app's block page when a navigation to a blocked domain starts during an active block window, before the request is made.

#### Scenario: Blocked site redirected
- **WHEN** the user navigates to `reddit.com` during an active block window
- **THEN** the tab shows the block page instead of loading the site

#### Scenario: Site with a service worker is still redirected
- **WHEN** the user navigates to `youtube.com` during an active block window
- **THEN** the tab shows the block page instead of YouTube's own offline page

#### Scenario: Ordinary failure not redirected
- **WHEN** the user navigates to a domain that is not on the block list and the connection fails
- **THEN** the tab shows the browser's normal error page
