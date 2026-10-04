## ADDED Requirements

### Requirement: Time format can be chosen
The system SHALL offer the time formats Follow Windows, 24-hour and 12-hour in a Language and time section of the Settings tab, below Appearance, and SHALL use Follow Windows when none has been chosen. Follow Windows SHALL use 12-hour when Windows' short time format shows hours from 1 to 12, and 24-hour otherwise, including when Windows' setting cannot be read.

#### Scenario: Windows uses 24-hour time
- **WHEN** the time format is Follow Windows and Windows' short time format is `HH:mm`
- **THEN** Blocky shows 17:00 as "17:00"

#### Scenario: Windows uses 12-hour time
- **WHEN** the time format is Follow Windows and Windows' short time format is `h:mm tt`
- **THEN** Blocky shows 17:00 as "5:00 PM"

#### Scenario: 12-hour chosen
- **WHEN** the user picks 12-hour while Windows uses 24-hour time
- **THEN** Blocky shows 17:00 as "5:00 PM", and 12-hour is still chosen after Blocky is restarted

### Requirement: Clock times follow the time format
The system SHALL show every clock time in the chosen format: the "unblocked until" lines on the Status tab, the time of each entry and the times in schedule details on the History tab, the end time on the block page, and the schedule's start and end fields. In 12-hour format the schedule fields SHALL take an hour from 1 to 12 with an AM/PM switch, and SHALL save the same 24-hour time as before, so 12:30 AM is saved as 00:30 and 12:30 PM as 12:30. Durations, such as the time remaining on the Status tab, SHALL NOT change.

#### Scenario: Override line in 12-hour format
- **WHEN** the time format is 12-hour and `reddit.com` is overridden until 17:00
- **THEN** the Status tab reads "reddit.com unblocked until 5:00 PM" with the time left unchanged

#### Scenario: Block page in 12-hour format
- **WHEN** the time format is 12-hour and `reddit.com` is blocked until 17:00
- **THEN** the block page reads "reddit.com is blocked until 5:00 PM"

#### Scenario: Schedule typed in 12-hour format
- **WHEN** the time format is 12-hour and the user sets the schedule from 9:00 AM to 5:30 PM and saves it
- **THEN** the schedule is stored as 09:00 to 17:30 and blocking happens between those times

#### Scenario: Schedule fields after a format change
- **WHEN** the schedule is 09:00 to 17:00 and the user switches the time format from 24-hour to 12-hour
- **THEN** the schedule fields show 9:00 AM and 5:00 PM

### Requirement: First day of the week can be chosen
The system SHALL offer Follow Windows, Monday, Saturday and Sunday as the first day of the week in the Language and time section, and SHALL use Follow Windows when none has been chosen. Follow Windows SHALL use the first day of the week set in Windows, whichever day that is, and Monday when it cannot be read.

#### Scenario: Windows starts the week on Sunday
- **WHEN** the first day of the week is Follow Windows and Windows starts the week on Sunday
- **THEN** Blocky starts the week on Sunday

#### Scenario: Monday chosen
- **WHEN** the user picks Monday while Windows starts the week on Sunday
- **THEN** Blocky starts the week on Monday, and Monday is still chosen after Blocky is restarted

### Requirement: Days are listed from the first day of the week
The system SHALL list the day boxes on the Schedule tab, and the days in schedule details on the History tab, starting from the first day of the week, and SHALL group days that follow each other in that order. The chosen first day SHALL NOT change which days are blocked.

#### Scenario: Schedule tab with Sunday first
- **WHEN** the week starts on Sunday
- **THEN** the Schedule tab shows the day boxes in the order Sun, Mon, Tue, Wed, Thu, Fri, Sat, with the same days ticked as before

#### Scenario: Days that run across the end of a Monday week
- **WHEN** the week starts on Sunday and the schedule is Sunday to Tuesday
- **THEN** the History tab describes the days as "Sun–Tue"

### Requirement: History follows the current settings
The system SHALL show earlier History entries in the current time format and first day of the week, including schedule changes saved before this setting existed when their details follow the earlier pattern of days followed by a start and end time. Details that do not follow that pattern SHALL be shown as stored.

#### Scenario: Earlier schedule change after a format change
- **WHEN** a schedule change was recorded as "Mon–Fri, 09:00–17:00" and the time format is now 12-hour
- **THEN** the History tab shows its details as "Mon–Fri, 9:00 AM–5:00 PM"

### Requirement: Reset to default puts every setting back
The system SHALL offer Reset to default in the Settings tab, which at once puts every setting back to its default, and SHALL NOT change the block list, schedule, shortlist, overrides or history. After a reset the system SHALL show a message that the settings were reset, with an Undo action that restores the settings from before the reset; the message and Undo SHALL stay until another setting is changed.

#### Scenario: Settings reset
- **WHEN** the user has chosen Blossom, Georgia and Large, and presses Reset to default
- **THEN** the window uses Forest, Segoe UI Variable and Normal, a message with Undo is shown, and the block list, schedule and shortlist are unchanged

#### Scenario: Time settings reset
- **WHEN** the user has chosen 12-hour time and Sunday as the first day, and presses Reset to default
- **THEN** both are back to Follow Windows

#### Scenario: Reset undone
- **WHEN** the user presses Undo after a reset
- **THEN** the window uses Blossom, Georgia and Large again, and those settings are saved

#### Scenario: Undo ends with the next change
- **WHEN** the user picks another theme after a reset
- **THEN** the reset message and its Undo are no longer shown

## REMOVED Requirements

### Requirement: Reset to default
**Reason**: Start with Windows moved to a later installer level, so the exception for it and its scenario no longer apply; the requirement continues as "Reset to default puts every setting back" with the time settings added.
**Migration**: None; Reset behaves as before for the appearance settings and now also resets the time settings.
