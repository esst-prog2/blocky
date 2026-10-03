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
