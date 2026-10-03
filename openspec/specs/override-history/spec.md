# override-history Specification

## Purpose
Lets the user review past overrides in the app, so that the record of deliberate exceptions is visible and not only stored on disk.

## Requirements

### Requirement: History tab lists past overrides
The system SHALL provide a History tab that lists every recorded override, showing domain, timestamp, and reason.

#### Scenario: Overrides listed
- **WHEN** the user opens the History tab after two overrides
- **THEN** both overrides are listed with their domain, timestamp, and reason

#### Scenario: Empty history
- **WHEN** no override has been recorded
- **THEN** the History tab shows an empty list without an error

### Requirement: History lists every change
The system SHALL record and list in the History tab every change the user makes: a site added, edited or removed; a suggestion added, edited or removed; the schedule changed; an override; and an override undone. Each entry SHALL show when it happened, what kind of change it was, the item it concerns, and details such as the reason or the old and new value.

#### Scenario: Site edited
- **WHEN** the user edits `chess.com` to `lichess.org`
- **THEN** the History tab gains an entry "Site edited" for `lichess.org` with the details `chess.com → lichess.org`

#### Scenario: Schedule changed
- **WHEN** the user saves the schedule as Monday to Friday, 09:00 to 17:00, after it was different
- **THEN** the History tab gains an entry "Schedule changed" with the details `Mon–Fri, 09:00–17:00`

#### Scenario: Suggestion removed
- **WHEN** the user removes the suggestion "10-minute walk"
- **THEN** the History tab gains an entry "Suggestion removed" for "10-minute walk"

### Requirement: History is shown as aligned columns, newest first
The system SHALL show the history as a table with the columns When, Event, Item and Details, aligned from row to row, with the newest entry at the top.

#### Scenario: Two changes
- **WHEN** the user adds `reddit.com` and then overrides it
- **THEN** the History tab shows the override above the site being added, and both rows' columns line up
