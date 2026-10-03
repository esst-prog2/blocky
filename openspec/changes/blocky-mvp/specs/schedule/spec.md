## Purpose

Defines the single weekly time window during which the block list is active, so that blocking follows a predictable routine set by the user.

## ADDED Requirements

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
