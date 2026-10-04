## ADDED Requirements

### Requirement: Language can be chosen
The system SHALL offer the languages Follow Windows, English, Nederlands and Magyar in the Language and time section of the Settings tab, above the time format, with each language named in that language, and SHALL use Follow Windows when none has been chosen. Below the row the system SHALL name the language Windows uses when it is one of the three, and otherwise say that Windows uses another language, so Follow Windows gives English. A changed language SHALL take effect in the window at once and SHALL be kept after Blocky is restarted.

#### Scenario: Dutch chosen
- **WHEN** the user picks Nederlands while Windows uses English
- **THEN** the window is shown in Dutch at once, the Settings tab is still selected, and Nederlands is still chosen after Blocky is restarted

#### Scenario: Language names stay in their own language
- **WHEN** the window is shown in Hungarian
- **THEN** the language choices read Follow Windows in Hungarian, then English, Nederlands and Magyar

### Requirement: Follow Windows uses Windows' display language
With Follow Windows chosen, the system SHALL use Dutch when Windows' display language is Dutch, Hungarian when it is Hungarian, whatever the region, and English for every other display language and when the display language cannot be read. The system SHALL read Windows' display language when it starts and before the window is redrawn after a settings change.

#### Scenario: Windows in Dutch
- **WHEN** the language is Follow Windows and Windows' display language is Dutch (Belgium)
- **THEN** Blocky is shown in Dutch

#### Scenario: Windows in a language Blocky does not have
- **WHEN** the language is Follow Windows and Windows' display language is French
- **THEN** Blocky is shown in English

### Requirement: Every shown text is in the chosen language
The system SHALL show every text it writes in the chosen language: tab names, section titles and captions, buttons, placeholders, hints, messages and errors in the window, the warning banner, the message shown when Blocky is started without administrator rights, and the block page, which SHALL also declare its language to the browser. The system SHALL NOT translate the name Blocky, font names, domains, or text the user typed, such as suggestions and override reasons. With English chosen, every text SHALL be the same as before languages existed.

#### Scenario: Status in Hungarian
- **WHEN** the language is Magyar and no block window is active
- **THEN** the Status tab says in Hungarian that nothing is blocked right now

#### Scenario: Error in Dutch
- **WHEN** the language is Nederlands and the user saves a schedule with no days ticked
- **THEN** the message asking to pick at least one day is shown in Dutch

#### Scenario: Block page in Dutch
- **WHEN** the language is Nederlands and `reddit.com` is blocked until 17:00
- **THEN** the block page reads "reddit.com is geblokkeerd tot 17:00", is marked as Dutch, and shows the suggestions as typed

#### Scenario: English unchanged
- **WHEN** the language is English
- **THEN** every text in the window and on the block page reads exactly as before this setting existed

### Requirement: Dates and times follow the language
The system SHALL write day names, month names and the date and time of History entries in the conventions of the chosen language, and SHALL write the hours and minutes of durations with that language's units. In 12-hour format the system SHALL use that language's markers for before and after noon, in the schedule fields too. The time format and first day of the week SHALL NOT depend on the language.

#### Scenario: History date in each language
- **WHEN** an entry was recorded on Sunday 4 October 2026 at 17:05 and the time format is 24-hour
- **THEN** the History tab shows its time as "Sun 4 Oct 2026, 17:05" in English, "zo 4 okt 2026, 17:05" in Dutch and "2026. okt. 4. (V), 17:05" in Hungarian

#### Scenario: 12-hour time in Hungarian
- **WHEN** the language is Magyar, the time format is 12-hour and `reddit.com` is blocked until 17:00
- **THEN** the block page shows the end time as "du. 5:00"

#### Scenario: Day boxes in Dutch
- **WHEN** the language is Nederlands and the week starts on Monday
- **THEN** the Schedule tab shows the day boxes as ma, di, wo, do, vr, za, zo

## MODIFIED Requirements

### Requirement: History follows the current settings
The system SHALL show earlier History entries in the current language, time format and first day of the week: event names, and the days and times of schedule changes, including schedule changes saved before these settings existed when their details follow the earlier pattern of English day names followed by a start and end time. Details that do not follow that pattern, and text the user typed, SHALL be shown as stored.

#### Scenario: Earlier schedule change after a format change
- **WHEN** a schedule change was recorded as "Mon–Fri, 09:00–17:00" and the time format is now 12-hour
- **THEN** the History tab shows its details as "Mon–Fri, 9:00 AM–5:00 PM"

#### Scenario: Earlier entries after a language change
- **WHEN** a site was added and the schedule was changed to "Mon–Fri, 09:00–17:00" while the language was English, and the language is now Nederlands
- **THEN** the History tab shows both events with Dutch names and the schedule details as "ma–vr, 09:00–17:00"

### Requirement: Reset to default puts every setting back
The system SHALL offer Reset to default in the Settings tab, which at once puts every setting back to its default, and SHALL NOT change the block list, schedule, shortlist, overrides or history. After a reset the system SHALL show a message that the settings were reset, with an Undo action that restores the settings from before the reset; the message and Undo SHALL stay until another setting is changed.

#### Scenario: Settings reset
- **WHEN** the user has chosen Blossom, Georgia and Large, and presses Reset to default
- **THEN** the window uses Forest, Segoe UI Variable and Normal, a message with Undo is shown, and the block list, schedule and shortlist are unchanged

#### Scenario: Time settings reset
- **WHEN** the user has chosen 12-hour time and Sunday as the first day, and presses Reset to default
- **THEN** both are back to Follow Windows

#### Scenario: Language reset
- **WHEN** the user has chosen Magyar while Windows' display language is English, and presses Reset to default
- **THEN** the language is back to Follow Windows, the window is shown in English, and the reset message and Undo are in English

#### Scenario: Reset undone
- **WHEN** the user presses Undo after a reset
- **THEN** the window uses Blossom, Georgia and Large again, and those settings are saved

#### Scenario: Undo ends with the next change
- **WHEN** the user picks another theme after a reset
- **THEN** the reset message and its Undo are no longer shown
