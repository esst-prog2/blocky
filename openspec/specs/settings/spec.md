# settings Specification

## Purpose
Lets the user adjust how Blocky looks (theme, font and text size), how it writes times and weeks, and which language it speaks, from a Settings tab, so the app and its block page are comfortable to read for them.

## Requirements

### Requirement: Settings tab applies changes immediately
The system SHALL provide a Settings tab after the Shortlist tab, with the settings grouped in sections (Appearance first), that scrolls when its contents do not fit the window. A setting changed there SHALL take effect in the window at once and SHALL be saved without a separate Save action, and the Settings tab SHALL stay selected after the change.

#### Scenario: Theme changed
- **WHEN** the user picks the Navy theme in the Settings tab
- **THEN** the window shows the Navy colours, the Settings tab is still selected, and Navy is still chosen after Blocky is restarted

#### Scenario: Settings do not fit
- **WHEN** the text size is Extra large and the window is at its smallest size
- **THEN** every setting in the Settings tab can be reached by scrolling

### Requirement: Five themes, two dark and three light
The system SHALL offer the themes Forest and Navy (dark) and Sand, Aqua and Blossom (light), and SHALL use Forest when no theme has been chosen.

#### Scenario: Default theme
- **WHEN** Blocky starts for the first time
- **THEN** the window uses the Forest theme

#### Scenario: Light theme chosen
- **WHEN** the user picks the Aqua theme
- **THEN** the window background, cards, text and buttons use the Aqua colours

### Requirement: Every theme stays readable
Every theme SHALL give each text colour a contrast ratio of at least 4.5:1 against every surface it is shown on, and field borders and disabled buttons at least 3:1, as defined by WCAG 2.1.

#### Scenario: Text on a card
- **WHEN** body text, muted text, accent text, warning text or error text is shown on a card in any theme
- **THEN** its contrast ratio with the card is at least 4.5:1

### Requirement: Follow Windows theme
The system SHALL offer Follow Windows as a theme choice, together with a choice of one dark and one light theme for it. With Follow Windows chosen, the window SHALL use the chosen dark theme while Windows apps are set to dark mode and the chosen light theme while they are set to light mode, and SHALL switch within a few seconds when that Windows setting changes while Blocky is open. Without a choice, Follow Windows SHALL use Forest for dark and Sand for light.

#### Scenario: Windows in light mode
- **WHEN** Follow Windows is chosen with Navy for dark and Blossom for light, and Windows apps are set to light mode
- **THEN** the window uses the Blossom theme

#### Scenario: Windows switches to dark mode
- **WHEN** Follow Windows is chosen and the user switches Windows apps to dark mode while Blocky is open
- **THEN** the window changes to the chosen dark theme within a few seconds

### Requirement: Font can be chosen
The system SHALL offer the fonts Segoe UI Variable, Segoe UI, Bahnschrift, Calibri, Candara, Corbel, Verdana, Tahoma, Georgia and Constantia, SHALL show each font's name in that font in the list, and SHALL use Segoe UI Variable when none has been chosen.

#### Scenario: Font chosen
- **WHEN** the user picks Georgia
- **THEN** all text in the window is shown in Georgia

### Requirement: Text size can be chosen
The system SHALL offer the text sizes Small, Normal, Large and Extra large, which show all text at 90, 100, 115 and 130 percent of the normal size, and SHALL use Normal when none has been chosen.

#### Scenario: Larger text
- **WHEN** the user picks Extra large
- **THEN** all text in the window is shown at 130 percent of its normal size

### Requirement: Stored settings fall back to defaults when invalid
The system SHALL store the settings with the rest of Blocky's data. A stored setting that is missing or not one of the offered choices SHALL be replaced by its default without affecting the other settings or the rest of the data, and SHALL NOT count as a damaged configuration.

#### Scenario: Unknown theme in the stored settings
- **WHEN** the stored theme is "Purple" and the stored font is Calibri
- **THEN** Blocky starts with the Forest theme and Calibri, without a warning, and keeps the block list

### Requirement: Window icon follows the theme
The system SHALL show an icon in the colours of the current theme as the window and taskbar icon, and SHALL change it when the theme changes.

#### Scenario: Icon after a theme change
- **WHEN** the user picks the Sand theme
- **THEN** the window and taskbar show the Sand icon

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
