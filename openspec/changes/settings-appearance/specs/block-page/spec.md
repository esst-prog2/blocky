## ADDED Requirements

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
