## REMOVED Requirements

### Requirement: Schedule times are picked from hour and minute menus
**Reason**: The menus were long and awkward; guarded time fields give the same guarantee more compactly.
**Migration**: None needed; saved schedules keep their `HH:MM` times and are shown in the new fields.

## ADDED Requirements

### Requirement: Schedule times are typed into guarded hour and minute fields
The system SHALL show each schedule time as an hour field and a minute field that accept only digits, at most two, and only values from 00 to 23 for the hour and 00 to 59 for the minute, ignoring any other keystroke. The arrow keys and mouse wheel SHALL step the value with wrap-around. Leaving a field SHALL pad a single digit to two, and leaving it empty SHALL restore its previous value. The time SHALL be stored as `HH:MM`.

#### Scenario: Valid time typed
- **WHEN** the user types `9` in the start hour and `05` in the start minute and saves
- **THEN** the schedule is saved with the start time `09:05` and the hour field shows `09`

#### Scenario: Invalid keystrokes ignored
- **WHEN** the user types `2a5` into an hour field
- **THEN** the field shows `2`

#### Scenario: Field left empty
- **WHEN** the user empties the end hour field and saves
- **THEN** the end time keeps its previous value

#### Scenario: Saved time shown
- **WHEN** the app opens with a saved schedule from 09:00 to 17:58
- **THEN** the fields show `09 : 00` and `17 : 58`
