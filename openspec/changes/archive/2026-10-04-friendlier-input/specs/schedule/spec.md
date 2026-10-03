## ADDED Requirements

### Requirement: Schedule times are entered as hours and minutes
The system SHALL accept a schedule time written as `H:MM` or `HH:MM` with a valid hour and minute, store it as `HH:MM`, and reject anything else with the message "Use a time like 09:00".

#### Scenario: Single-digit hour
- **WHEN** the user sets the start time to `9:00`
- **THEN** the schedule is saved with the start time `09:00`

#### Scenario: Not a time
- **WHEN** the user sets the start time to `nine`
- **THEN** the schedule is not saved and the message "Use a time like 09:00" is shown

### Requirement: Schedule needs at least one weekday
The system SHALL refuse to save a schedule from the app when no weekday is selected, and SHALL show the message "Pick at least one day".

#### Scenario: No weekday selected
- **WHEN** the user clears every weekday and saves the schedule
- **THEN** the schedule is not saved and the message "Pick at least one day" is shown
