## REMOVED Requirements

### Requirement: Schedule times are entered as hours and minutes
**Reason**: Times are no longer typed, so there is no text to accept or reject; hour and minute menus replace the text fields.
**Migration**: None needed; saved schedules keep their `HH:MM` times and are shown in the new menus.

## ADDED Requirements

### Requirement: Schedule times are picked from hour and minute menus
The system SHALL let the user pick each schedule time from an hour menu (00 to 23) and a minute menu (00 to 59), so that only valid times can be entered, and SHALL store the time as `HH:MM`.

#### Scenario: Time picked from the menus
- **WHEN** the user picks hour `09` and minute `05` as the start time and saves
- **THEN** the schedule is saved with the start time `09:05`

#### Scenario: Saved time shown in the menus
- **WHEN** the app opens with a saved schedule from 09:00 to 17:58
- **THEN** the start menus show `09` and `00`, and the end menus show `17` and `58`
