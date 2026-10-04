## Why

Blocky only speaks English. The owner and the people around them read Dutch and Hungarian more easily, and a tool that is meant to be calm and low-friction should not make anyone read a second language while they are trying to focus. This is part 3 of the Settings feature, narrowed to English, Hungarian and Dutch (decided 2026-10-04); like the time settings it follows Windows until the user chooses.

## What Changes

- A **Language** setting in the Language and time section, above Time format: Follow Windows (default), English, Nederlands and Magyar, each language named in itself. A line under the row names Windows' display language, as the time rows do.
- **Follow Windows** uses Windows' display language when it is Dutch or Hungarian (any region), and English for every other language or when it cannot be read. It is read at start and before every redraw, like the time settings.
- **Every text Blocky shows is translated**: tabs, titles, captions, buttons, placeholders, hints and error messages in the window; event names, day names and schedule details on the History tab; the warning banner; the administrator message box at start; and the block page. Kept as they are: the name Blocky, font names, domains, and what the user typed (suggestions, override reasons). Theme names are translated.
- **Dates and times per language** on the History tab (for example "Sun 4 Oct 2026, 17:05", "zo 4 okt 2026, 17:05", "2026. okt. 4. (V), 17:05"), day names on the Schedule tab and in the Settings captions, the AM/PM markers in 12-hour time, and the hours-and-minutes durations on the Status tab.
- **History follows the current language**, as it already follows the time format: events are stored by type, and schedule changes as days and times, so earlier entries are shown in the language chosen later. Earlier schedule text that cannot be read back stays as stored.
- **Reset to default** also puts the language back to Follow Windows.
- **Not translated**: `errors.log` (kept in English for troubleshooting), the browser extension's description, and the README.

## Capabilities

### New Capabilities

### Modified Capabilities
- `settings`: new requirements for choosing the language, following Windows' display language, translating every shown text including the block page, and dates per language; the History and Reset to default requirements are replaced by versions that include the language.

## Impact

- New `blocky/language.py`: the current language, the translation tables for Dutch and Hungarian, and reading Windows' display language.
- `blocky/settings.py`: a `language` field with Follow Windows as default and per-field fallback.
- `blocky/clock.py`, `blocky/history.py`: day and month names, AM/PM markers and the History date in the current language.
- `blocky/app.py`, `blocky/timefield.py`, `blocky/domainfield.py`, `blocky/suggestions.py`, `blocky/domains.py`, `blocky/schedule.py`, `blocky/rules.py`, `blocky/controller.py`, `blocky/config.py`: shown texts go through the translation function.
- `blocky/server.py`, `blocky/__main__.py`: the block page in the chosen language (`lang` attribute included); the language passed in the page state; the administrator message in the stored or Windows language.
- Tests: the open_app fixture pins Windows' language to English (as it pins the time settings), so existing tests keep their English texts; new tests for each language. No change to the extension, the stored schedule, or `/api/state` fields the extension reads.
