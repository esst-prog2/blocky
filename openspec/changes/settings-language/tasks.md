## 1. Pin today's English

- [x] 1.1 Add a test that collects every text the window shows on each tab (labels, buttons, placeholders, captions, the History table with sample events, the Status lines with an override) and the block page with and without a block, and compares it with a stored English list; verify it passes before any other change and fails when one text is changed

## 2. Language module and setting

- [x] 2.1 Add `blocky/language.py` with `LANGUAGES`, empty `NL`/`HU` tables, `apply`, `translate`, `_` (named placeholders) and `marked`, and `windows_language()` with a pure LANGID mapping; verify with tests that English returns the text unchanged, placeholders fill in every language, a missing entry falls back to English, and LANGIDs for nl-NL, nl-BE, hu-HU, en-US, fr-FR and a failing call map to nl, nl, hu, en, en, en
- [x] 2.2 Add `language` to `Settings` (Follow Windows default, choices en/nl/hu, per-field fallback) and `effective_language(settings, windows)`; verify with tests for every combination and that a part-2 config loads with Follow Windows and saves unchanged apart from the new field
- [x] 2.3 Add the coverage test: an `ast` scan of `blocky/` for literals passed to `_()`, `translate()` and `marked()`, checking each has a Dutch and a Hungarian entry with the same placeholders and that no table entry is unused; verify it fails on a missing and on an unused entry (it fails until group 4 is done)

## 3. Dates, days and times per language

- [x] 3.1 Add `language` to `TimeStyle` and per-language tables in `clock.py` (short and full day names, short month names, AM/PM markers and their position), `format_duration`, and a History date without `%a`/`%b`; verify with tests for the table in design.md in all three languages, 12-hour 00:00, 12:00 and 17:05 in each, the day boxes ma…zo and H…V, and that the English output equals the pinned output from part 2
- [x] 3.2 Keep stored text English: new schedule events store English `details` and older text is parsed as English, then shown in the current language; verify with tests that a "Mon–Fri, 09:00–17:00" event shows as "ma–vr, 09:00–17:00" in Dutch and "H–P, 09:00–17:00" in Hungarian, and that the details stored for a new event are English whatever the language
- [x] 3.3 Give `history.Row` the event type and colour override rows by type; verify with a window test that an override row in Dutch still uses the accent colour

## 4. Translate every text

- [x] 4.1 Route every shown text in `app.py`, `timefield.py`, `domainfield.py`, `suggestions.py`, `domains.py`, `schedule.py`, `rules.py`, `controller.py`, `hosts.py`, `config.py`, `history.py` and `__main__.py` through `_()` or `marked()`, leaving `errors.log` text English; verify the English pin test from 1.1 still passes unchanged
- [x] 4.2 Write the Dutch and Hungarian tables, including theme and text size names; verify the coverage test from 2.3 passes
- [x] 4.3 Add the leftover-English test: render every tab and the block page in Dutch and in Hungarian and fail on any shown text equal to its English form outside the allow-list (Blocky, font names, domains, typed text, language names); verify it passes and fails when one `_()` is removed

## 5. Window

- [x] 5.1 Inject `windows_language` into `App` (pinned to English in `open_app`), apply the language in `_apply_settings`, and add the Language row above Time format with its caption; verify with window tests that picking Nederlands shows the window in Dutch at once on the Settings tab and is kept after reopening, that Follow Windows with Windows in Hungarian shows Hungarian and with French shows English and the "another language" caption, and that Reset puts the language back to Follow Windows with the reset message in English
- [x] 5.2 Check the layout in each language; verify with a window test that at Extra large and the smallest window size every tab and button in Dutch and Hungarian shows its full text and the six tabs fit, shortening translations where they do not

## 6. Block page and start-up

- [x] 6.1 Add `"language"` to the page state and render the block page with `translate(..., code)` and `<html lang="...">`, falling back to English for a missing or unknown code; verify with server tests for the three languages ("reddit.com is geblokkeerd tot 17:00", Hungarian with "du. 5:00" in 12-hour), the not-blocked text, the empty shortlist text, and that `/api/state` keeps the fields the extension reads (run the extension tests)
- [x] 6.2 Apply the stored or Windows language in `main()` before the administrator check, so the administrator message and the start-up warnings use it; verify with tests that `ADMIN_NEEDED` and the damaged-config warning come out in Dutch when the stored language is nl, and that `errors.log` gets the English text

## 7. Checks, review and record

- [x] 7.1 Run ruff check, ruff format --check, mypy, pytest and the extension tests as separate commands and verify all pass
- [ ] 7.2 Run `tools/mutation_test.py` on `language` and `clock` (add `language` to its module list) and add tests for real gaps
- [x] 7.3 Generate `openspec/changes/settings-language/translations.md` (English, Dutch, Hungarian and where each appears) for the owner; verify it lists every table entry
- [ ] 7.4 Owner review of the Dutch and Hungarian texts from `translations.md`, with corrections applied to the tables and the table regenerated
- [ ] 7.5 Manual check by the owner: each language in the window and on the block page in Brave, Follow Windows after changing Windows' display language (then restarting Blocky), History after a language change, the administrator message in Dutch, and Reset to default
- [ ] 7.6 Log the decisions in `PLANNING_LOG.md`, update the README, and archive this change
