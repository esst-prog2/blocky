## Purpose

Lets the user adjust how Blocky looks (theme, font and text size) from a Settings tab, so the app and its block page are comfortable to read for them.

## ADDED Requirements

### Requirement: Settings tab applies changes immediately
The system SHALL provide a Settings tab after the Shortlist tab, with the settings grouped in sections (Appearance first), that scrolls when its contents do not fit the window. A setting changed there SHALL take effect in the window at once and SHALL be saved without a separate Save action, and the Settings tab SHALL stay selected after the change.

#### Scenario: Theme changed
- **WHEN** the user picks the Navy theme in the Settings tab
- **THEN** the window shows the Navy colours, the Settings tab is still selected, and Navy is still chosen after Blocky is restarted

#### Scenario: Settings do not fit
- **WHEN** the text size is Extra large and the window is at its smallest size
- **THEN** every setting in the Settings tab can be reached by scrolling

### Requirement: Five themes, two dark and three light
The system SHALL offer the themes Forest and Navy (dark) and Sand, Aqua and Blossom (light), and SHALL use Forest when no theme has been chosen.

#### Scenario: Default theme
- **WHEN** Blocky starts for the first time
- **THEN** the window uses the Forest theme

#### Scenario: Light theme chosen
- **WHEN** the user picks the Aqua theme
- **THEN** the window background, cards, text and buttons use the Aqua colours

### Requirement: Every theme stays readable
Every theme SHALL give each text colour a contrast ratio of at least 4.5:1 against every surface it is shown on, and field borders and disabled buttons at least 3:1, as defined by WCAG 2.1.

#### Scenario: Text on a card
- **WHEN** body text, muted text, accent text, warning text or error text is shown on a card in any theme
- **THEN** its contrast ratio with the card is at least 4.5:1

### Requirement: Follow Windows theme
The system SHALL offer Follow Windows as a theme choice, together with a choice of one dark and one light theme for it. With Follow Windows chosen, the window SHALL use the chosen dark theme while Windows apps are set to dark mode and the chosen light theme while they are set to light mode, and SHALL switch within a few seconds when that Windows setting changes while Blocky is open. Without a choice, Follow Windows SHALL use Forest for dark and Sand for light.

#### Scenario: Windows in light mode
- **WHEN** Follow Windows is chosen with Navy for dark and Blossom for light, and Windows apps are set to light mode
- **THEN** the window uses the Blossom theme

#### Scenario: Windows switches to dark mode
- **WHEN** Follow Windows is chosen and the user switches Windows apps to dark mode while Blocky is open
- **THEN** the window changes to the chosen dark theme within a few seconds

### Requirement: Font can be chosen
The system SHALL offer the fonts Segoe UI Variable, Segoe UI, Bahnschrift, Calibri, Candara, Corbel, Verdana, Tahoma, Georgia and Constantia, SHALL show each font's name in that font in the list, and SHALL use Segoe UI Variable when none has been chosen.

#### Scenario: Font chosen
- **WHEN** the user picks Georgia
- **THEN** all text in the window is shown in Georgia

### Requirement: Text size can be chosen
The system SHALL offer the text sizes Small, Normal, Large and Extra large, which show all text at 90, 100, 115 and 130 percent of the normal size, and SHALL use Normal when none has been chosen.

#### Scenario: Larger text
- **WHEN** the user picks Extra large
- **THEN** all text in the window is shown at 130 percent of its normal size

### Requirement: Reset to default
The system SHALL offer Reset to default in the Settings tab, which at once puts every setting back to its default, except whether Blocky starts with Windows, and SHALL NOT change the block list, schedule, shortlist, overrides or history. After a reset the system SHALL show a message that the settings were reset, with an Undo action that restores the settings from before the reset; the message and Undo SHALL stay until another setting is changed.

#### Scenario: Settings reset
- **WHEN** the user has chosen Blossom, Georgia and Large, and presses Reset to default
- **THEN** the window uses Forest, Segoe UI Variable and Normal, a message with Undo is shown, and the block list, schedule and shortlist are unchanged

#### Scenario: Reset undone
- **WHEN** the user presses Undo after a reset
- **THEN** the window uses Blossom, Georgia and Large again, and those settings are saved

#### Scenario: Undo ends with the next change
- **WHEN** the user picks another theme after a reset
- **THEN** the reset message and its Undo are no longer shown

#### Scenario: Start with Windows is kept
- **WHEN** Blocky is set to start with Windows and the user presses Reset to default
- **THEN** Blocky still starts with Windows, and the reset message says so

### Requirement: Stored settings fall back to defaults when invalid
The system SHALL store the settings with the rest of Blocky's data. A stored setting that is missing or not one of the offered choices SHALL be replaced by its default without affecting the other settings or the rest of the data, and SHALL NOT count as a damaged configuration.

#### Scenario: Unknown theme in the stored settings
- **WHEN** the stored theme is "Purple" and the stored font is Calibri
- **THEN** Blocky starts with the Forest theme and Calibri, without a warning, and keeps the block list

### Requirement: Window icon follows the theme
The system SHALL show an icon in the colours of the current theme as the window and taskbar icon, and SHALL change it when the theme changes.

#### Scenario: Icon after a theme change
- **WHEN** the user picks the Sand theme
- **THEN** the window and taskbar show the Sand icon
