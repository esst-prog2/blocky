## Purpose

Lets the user review past overrides in the app, so that the record of deliberate exceptions is visible and not only stored on disk.

## ADDED Requirements

### Requirement: History tab lists past overrides
The system SHALL provide a History tab that lists every recorded override, showing domain, timestamp, and reason.

#### Scenario: Overrides listed
- **WHEN** the user opens the History tab after two overrides
- **THEN** both overrides are listed with their domain, timestamp, and reason

#### Scenario: Empty history
- **WHEN** no override has been recorded
- **THEN** the History tab shows an empty list without an error
