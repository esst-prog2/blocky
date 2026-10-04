## Context

Every shown text is an English string literal where it is used: about 90 in `app.py`, the event names in `history.EVENTS`, the hints and `ValueError` messages in `domainfield.py`, `suggestions.py`, `domains.py`, `schedule.py`, `rules.py`, `controller.py` and `hosts.py`, the start-up warnings in `config.py` and `__main__.py`, and the block page in `server.py`. Error messages reach the window as `str(error)` through `App._attempt`; hosts errors reach the banner through `Checker.last_error` from the background thread. Day names come from `clock.DAY_NAMES` and `FULL_DAY_NAMES` in `app.py`; `history.when()` uses `%a` and `%b`, which follow the C locale. `TimeStyle` (part 2) carries the time format and first day and is passed to every formatting function and, as `timeStyle`, to the block page. Settings apply through `App._apply_settings` before each redraw; `theme.apply()` sets module-level state that widgets read when they are built. History stores events by type and new schedule changes as days and times (part 2), with English `details` kept for older versions. `App._history_row` colours the event cell by `text.startswith("Override")`.

## Goals / Non-Goals

**Goals:**
- One translation function, so a shown text is written once in English where it is used and looked up for Dutch and Hungarian.
- A test that fails when a text has no Dutch or Hungarian translation, so a later change cannot add an untranslated text unnoticed.
- English output identical to today, so the existing tests stay as they are.

**Non-Goals:**
- Changing a language while a warning is already in the banner: warnings made at start stay in the language Blocky started in.
- Translating messages that come from Windows inside an error (for example "Access is denied"); Windows already writes them in its own language.
- Right-to-left layout, plural rules beyond what these three languages need here, and the extension's text.

## Decisions

### English text as the key, tables in Python
New `blocky/language.py` holds `LANGUAGES = ("en", "nl", "hu")`, the tables `NL` and `HU` (dicts from the English text to the translation), the current language, `apply(code)`, `translate(text, code, **values)` and `_(text, **values)`, which translates into the current language and fills named placeholders with `str.format`. Call sites read `_("Add a site")` and `_("{domain} is already in the list", domain=domain)`; named placeholders let Hungarian put the words in its own order ("{domain} {time}-ig tiltva van").

Alternative considered: gettext with `.po` files. Rejected: it needs a compile step to `.mo` files (no `msgfmt` in the project), adds files the owner has to learn, and a project with about 150 texts gains nothing from it. Alternative considered: keys like `status.nothing_blocked`. Rejected: the code would no longer show what the user reads.

A test walks the source with `ast`, collects every literal passed to `_()` and `translate()`, and checks that each has an entry in `NL` and `HU` with the same placeholders, and that neither table has entries no code uses. Calls with a non-literal text (the event names, theme and size labels) go through `marked(text)`, a no-op the same test also collects.

### Current language as module state, explicit where threads differ
`App._apply_settings` calls `language.apply(effective_language(settings, windows_language))` next to `theme.apply`, so widgets, hints and `ValueError` messages raised from the controller are made in the current language at the moment they are created, as the theme's colours are. The block page runs on server threads and gets its language from the page state (`"language": "nl"`) and calls `translate(..., code)` with it, never the module state. The background check reads the module state when it builds a hosts error; reading a string set by the window thread is safe in Python.

### Windows' display language
`windows_language()` in `language.py` calls `GetUserDefaultUILanguage` through `ctypes` and maps the primary language of the LANGID (`langid & 0x3FF`: `0x13` Dutch, `0x0E` Hungarian) to its code; every other value, and any failure (no `windll`, an exception), gives `"en"`. The mapping is a pure function, so every case is tested without Windows. Like `windows_time`, it is injected into `App` and read at start and before every redraw; `open_app` in `tests/conftest.py` pins it to English.

Alternative considered: `HKCU\Control Panel\International\LocaleName`. Rejected: that is the regional format, not the display language; someone with English Windows and Dutch regional settings would get Dutch.

### The setting
`Settings.language` with choices `follow-windows`, `en`, `nl`, `hu`, Follow Windows by default and the usual per-field fallback, so existing configs load with Follow Windows. `effective_language(settings, windows)` is pure. The setting sits above Time format as a drop-down list like the font's (decided at the owner's review), with "Follow Windows" (translated), "English", "Nederlands" and "Magyar"; the font list becomes one drop-down list class that both use. The caption names Windows' language in the current language ("Windows uses Dutch."), or, for any other language, says Windows uses another language so Follow Windows gives English; Blocky does not need names for languages it does not have.

### Dates, day names and AM/PM in `TimeStyle`
`TimeStyle` gains `language: str = "en"`, so the one style object already passed to `format_time`, `describe_days`, `describe_schedule`, `history.when` and the block page also carries how to write them. `clock.py` gets per-language tables: short and full day names, short month names, the before- and after-noon markers and whether they come first, and the date pattern for History:

| | Short days | 12-hour 17:00 | History date | Duration |
|---|---|---|---|---|
| en | Mon … Sun | 5:00 PM | Sun 4 Oct 2026, 17:05 | 2h 05m |
| nl | ma … zo | 5:00 p.m. | zo 4 okt 2026, 17:05 | 2u 05m |
| hu | H, K, Sze, Cs, P, Szo, V | du. 5:00 | 2026. okt. 4. (V), 17:05 | 2ó 05p |

`history.when()` stops using `%a`/`%b`, which depend on the C locale. `TimeField`'s AM/PM switch takes its labels from the same table; the stored time stays 24-hour. The durations on the Status tab and in the status line use a `format_duration(minutes, style)` in `clock.py`. `DEFAULT_STYLE` stays English, so the English `details` stored for new schedule changes and the parser for older text are unchanged: older text is always read as English and written in the current language.

### History by type, not by text
`history.Row` gains the event type, so `App._history_row` colours overrides by type instead of by the English text; the event name is `_()` of the English name at display time, so earlier entries follow a later language change.

### Start-up texts
`__main__.main` reads the stored settings (through `settings.from_data` on the loaded config, falling back to defaults on any error) and calls `language.apply` before the administrator check, so the administrator message box and the config and block page warnings are in the stored language, or Windows' under Follow Windows. `errors.log` keeps English: `log_error` gets English text, and the warning shown in the window is translated separately where both exist.

### Translations and review
The agent writes the Dutch and Hungarian tables. For the owner's check, a task generates `openspec/changes/settings-language/translations.md`: one table with English, Dutch and Hungarian side by side and the place each text appears. Corrections go into `NL`/`HU`; the table is regenerated, not edited by hand.

### Layout
Dutch and Hungarian texts are often longer ("Instellingen", "Beállítások", "Geschiedenis"). Buttons already grow to their text (part 2), and the tab buttons have a minimum of 96. A window test checks, for each language at Extra large and the smallest window size, that no tab or button shows less than its full text and that the six tabs fit in the window; where one does not, the translation is shortened rather than the layout changed.

## Risks / Trade-offs

- [A text is added later without `_()`] → the English text shows in every language; the scan test cannot see it. Mitigation: a test that renders every tab in Dutch and fails on any label, button or placeholder text that equals its English form, apart from a short allow-list (Blocky, font names, domains, "Aqua" if kept).
- [Translations read stiffly] → the owner checks Dutch and Hungarian from the review table before the change is archived.
- [A Hungarian suffix after a 12-hour time ("du. 5:00-ig")] → acceptable; it is how Hungarian writes it.
- [Warnings made at start keep the start language after a language change] → rare and cleared by a restart; noted in the Non-Goals.

## Migration Plan

Configs from part 2 get `language: follow-windows`. On a Dutch or Hungarian Windows the window switches language at the first start after the update; that is the decided behaviour. Stored events, schedules and overrides are unchanged; an older Blocky reading a newer config ignores the new field.
