# schedule Specification

## Purpose
Defines the single weekly time window during which the block list is active, so that blocking follows a predictable routine set by the user.

## Requirements

### Requirement: Weekly schedule is one time range on selected weekdays
The system SHALL store one weekly schedule consisting of a set of weekdays and one start and end time, and SHALL apply that time range to every selected weekday.

#### Scenario: Schedule applies to selected days
- **WHEN** the user selects Monday through Friday and sets 09:00 to 17:00
- **THEN** blocking is active on Monday through Friday between 09:00 and 17:00 and inactive otherwise

### Requirement: Schedule is shown unnamed
The system SHALL display the schedule with the label "Schedule" and SHALL NOT let the user name or save multiple schedules.

#### Scenario: Only one schedule exists
- **WHEN** the user opens the schedule settings
- **THEN** the app shows a single schedule labeled "Schedule" with no option to add another

### Requirement: Schedule changes take effect on the next check
The system SHALL apply a schedule change to blocking no later than the next background check.

#### Scenario: Changing the time range
- **WHEN** the user changes the end time from 17:00 to 18:00 while blocking is active
- **THEN** blocking remains active until 18:00 after the next background check

### Requirement: Schedule needs at least one weekday
The system SHALL refuse to save a schedule from the app when no weekday is selected, and SHALL show the message "Pick at least one day".

#### Scenario: No weekday selected
- **WHEN** the user clears every weekday and saves the schedule
- **THEN** the schedule is not saved and the message "Pick at least one day" is shown

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
