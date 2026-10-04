## 1. Themes as data

- [ ] 1.1 Add `THEMES` to `blocky/theme.py` with the role values from design.md (Forest unchanged, `SAGE` as Forest's `ACCENT`), and add `tests/test_theme.py` that checks every theme has every role and that every (text, surface) pair the window uses meets 4.5:1 (3:1 for borders and disabled buttons); verify the test fails when one value is made too pale
- [ ] 1.2 Add `theme.apply()` and make the helpers look colours up when called instead of in their default arguments; verify with a test that `label()`, `card()`, `quiet_button()`, `chip()` and `Message` created after `apply("navy")` use Navy colours
- [ ] 1.3 Make `font(role)` take family and scale from the current appearance (Segoe UI Variable keeps its Display/Text/Semibold families, other fonts use bold for display, brand, title and button), scale fixed control sizes with the text size, and verify with tests for every font and size

- [ ] 1.4 Pin today's look: a test that Forest's colour values, the default font roles (Segoe UI Variable Display/Text/Semibold) and the font sizes at Normal equal the values `theme.py` has before this change; verify it fails when one Forest value or size is changed

## 2. Settings storage

- [ ] 2.1 Add `blocky/settings.py` with the `Settings` dataclass, defaults, the list of themes, fonts and sizes, and `effective_theme(settings, windows_is_light)`; verify with tests for defaults and every combination of theme choice and Windows mode
- [ ] 2.2 Load and save a `settings` section in `blocky/config.py`; a missing section, a missing field, a wrong type or an unknown value falls back per field and never raises `DamagedConfig`; verify with tests per case, a round-trip test, and a property test that any YAML value in the section loads without an error
- [ ] 2.3 Keep existing configs working: a test with a config.yaml in today's format (no `settings` section, with sites, schedule, shortlist, overrides and events) that loads with default settings and every other value unchanged, and that saving it again keeps all of them; verify it also passes with `load_or_recover` and gives no warning
- [ ] 2.4 Add `Controller.set_settings()` and `Controller.reset_settings()`; verify that reset changes only the settings and leaves block list, schedule, shortlist, overrides and history as they were

## 3. Window

- [ ] 3.1 Add a redraw to `App` that rebuilds all tabs with the current theme, re-selects the open tab, repaints the title bar and sets the theme's icon; verify with a test that switches from Forest to every other theme and walks all widgets for leftover Forest colours, and that the open tab stays selected
- [ ] 3.2 Build the Settings tab as a scrollable frame with an Appearance section: theme tiles in each theme's own colours with Follow Windows and its dark and light choices, ten font buttons each shown in its own font, and the four text sizes; verify with window tests that each choice changes the window at once, is saved, and is still there after reopening the window
- [ ] 3.3 Add Reset to default with the "Settings reset." message and Undo; verify with window tests that reset restores the defaults without touching block list, schedule or shortlist, that Undo brings back and saves the earlier settings, that the message survives the redraw, and that it disappears after the next settings change
- [ ] 3.4 Poll Windows' app mode every 2 seconds while Follow Windows is chosen and redraw only when it changes; verify with a test that fakes the registry value and checks the switch, and that an unreadable value means dark
- [ ] 3.5 Open every tab at Extra large in every theme and verify with a test that the window builds without errors and that the Settings tab scrolls to its last row at the smallest window size; check by hand that nothing is clipped

## 4. Icons

- [ ] 4.1 Extend `tools/make_icons.py` to write `blocky/assets/blocky-<theme>.ico` for each theme (light themes: square in `PRIMARY`, letter in `ON_PRIMARY`), keeping `blocky.ico` and the extension PNGs as the Forest icon; verify the files exist and with a test that every theme has its icon file

## 5. Block page

- [ ] 5.1 Build the block page CSS from the effective theme, font and text size, and give the favicon link the theme name; serve the theme's icon at `/favicon.ico`; verify with server tests per theme for colours, font, size and favicon
- [ ] 5.2 Show the theme's icon next to Blocky on the block page and emphasise the domain (bold) and the end time (a chip); verify with server tests that both are marked up, that the domain is still HTML-escaped, and that the page contains no script

## 6. Checks and record

- [ ] 6.1 Run ruff check, ruff format --check, mypy, pytest and the extension tests and verify all pass
- [ ] 6.2 Run `tools/mutation_test.py` on `settings` and `theme` (add both to its module list) and add tests for any real gaps it finds
- [ ] 6.3 Manual check by the owner: every theme, font and size in the real window and on the block page in Brave, Follow Windows by switching Windows' mode, and Reset to default
- [ ] 6.4 Log the decisions in `PLANNING_LOG.md`, update the README, and archive this change
