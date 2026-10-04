## Context

All colours, fonts and sizes live in `blocky/theme.py` as module constants (`BACKGROUND`, `CARD`, `TEXT`, ...) and font roles, read by about 60 places in `blocky/app.py` when each widget is created. Nothing listens for changes afterwards. Several helpers take a colour as a default argument (`label(color=TEXT)`, `card(color=CARD)`, `quiet_button(color=SAGE)`, `chip(fg_color=BACKGROUND)`, `Message(color=MUTED)`); Python fixes those defaults once, when the module loads. The block page (`blocky/server.py`) has the Forest colours written into its CSS, and one icon (`blocky/assets/blocky.ico`) serves the window, the block page and, through the extension's PNGs, Brave.

## Goals / Non-Goals

**Goals:**
- One table of themes that the window, the block page, the icons and the contrast tests all read from.
- Switching a setting redraws the whole window correctly, with no widget left in old colours.
- Settings can never stop Blocky from starting.

**Non-Goals:**
- Recolouring widgets in place without a redraw.
- Fonts that do not come with Windows, or loading font files.
- Changing the Start-menu shortcut or extension icons.

## Decisions

### Themes are data: one role table per theme
`theme.py` holds `THEMES`, a mapping from theme name to its colour roles: `BACKGROUND`, `CARD`, `HOVER`, `BORDER`, `TEXT`, `MUTED`, `DEEP` (status card and selected tab), `ON_DEEP`, `SOFT_ON_DEEP`, `ACCENT` (brand name and text buttons), `PRIMARY`, `PRIMARY_HOVER`, `ON_PRIMARY`, `DISABLED`, `DISABLED_TEXT`, `WARNING`, `DANGER`. Forest keeps today's values; `SAGE` becomes `ACCENT` and `TEXT` on the status card becomes `ON_DEEP`. The values are those of the approved preview (Forest, Navy; light themes built by the 60-30-10 rule: lightest palette colour as background with near-white cards, middle tones for the status card and selected tab, the palette's strongest colour for the main button with dark text, and dark ink tinted with the palette's hue only for text and small details).

| role | Navy | Sand | Aqua | Blossom |
|---|---|---|---|---|
| BACKGROUND | #27374D | #FFFBE9 | #E3FDFD | #F9F5F6 |
| CARD | #2F4159 | #FFFDF6 | #F4FEFE | #FDFBFB |
| HOVER | #384C66 | #E3CAA5 | #CBF1F5 | #F8E8EE |
| BORDER | #7D93A5 | #81614B | #349298 | #85475E |
| TEXT | #DDE6ED | #2C1F17 | #0E3235 | #2D151E |
| MUTED | #9DB2BF | #624937 | #247175 | #663346 |
| DEEP | #526D82 | #E3CAA5 | #A6E3E9 | #FDCEDF |
| ON_DEEP | #FFFFFF | #2C1F17 | #0E3235 | #2D151E |
| SOFT_ON_DEEP | #F0F4F7 | #4F3A2C | #1C5A5E | #512938 |
| ACCENT | #9DB2BF | #8A3D24 | #196C70 | #602A3E |
| PRIMARY | #9DB2BF | #DB8E6E | #71C9CE | #F2BED1 |
| ON_PRIMARY | #27374D | #2C1F17 | #0E3235 | #2D151E |
| PRIMARY_HOVER | #B7C8D2 | #E1A288 | #8BD3D7 | #F4CAD9 |
| DISABLED | #3A4C63 | #E3CAA5 | #CBF1F5 | #F8E8EE |
| DISABLED_TEXT | #8D9FAE | #6F5849 | #387C80 | #724656 |
| WARNING | #E8B85C | #6B4500 | #6B4500 | #6B4500 |
| DANGER | #F09A8A | #A63A2B | #A63A2B | #A63A2B |

These are the values of the approved preview; the contrast test (below) checks all of them.

Alternative considered: deriving the light themes from the four palette colours at runtime. Rejected: a fixed table is easier to read, review and test, and the colours were chosen by eye.

### Switching by redraw, not by recolouring
`theme.apply(appearance)` sets the module's current role values and fonts; `App` then destroys its contents and builds them again with the same `_build_*` methods it uses at start, selects the tab that was open before anything is painted (so no other tab shows in between), repaints the Windows title bar and sets the theme's icon. Text typed but not yet added (a new site, a reason) is lost on a redraw; a settings change happens in the Settings tab, where nothing else is being typed.

Colour defaults in helper signatures become `None` and are looked up when the helper runs, so every helper call made after `apply` gets the new values. A test builds the window in one theme, switches to another, and walks every widget to check that no colour from the first theme is left.

Alternative considered: tracking each widget's colour role and calling `configure` on theme change. Rejected: it touches every widget creation in the app and silently misses any widget added later.

### The Settings tab is laid out for all four parts
The tab is a scrollable frame with sections: Appearance (this change), Language and time (parts 2 and 3) and Startup (part 4), with Reset to default at the bottom. Each later part adds rows to its own section without moving what is there. Reset puts every setting back to its default except the Startup setting, which changes Windows itself (a scheduled task) and would otherwise be switched off unnoticed by someone who only wanted the default colours back.

Reset acts at once and shows "Settings reset." with an Undo button (pattern: act, then offer undo, instead of asking first, so the common case is not interrupted). The app keeps the settings from before the reset in memory, not on disk; Undo saves them back and redraws. The message and the remembered settings are cleared by the next settings change, and also by closing Blocky. Since the redraw rebuilds the tab, the message is part of the state the redraw restores.

### Fonts and text size
`font(role)` keeps its roles (display, title, body, caption, button, brand) and takes family and scale from the current appearance. Segoe UI Variable keeps its separate Display, Text and Semibold families; for the other nine fonts, display and brand use the family in bold, title and button in bold, body and caption in normal weight. Sizes are multiplied by 0.9, 1.0, 1.15 or 1.3 and rounded. Fixed sizes (control height, chip height, wrap lengths) scale with the text size so larger text does not get clipped.

In the Settings tab the font is chosen from a drop-down list: a button showing the current font in itself opens a list under it (above it when there is no room) that shows four fonts at a time, each in its own font, and scrolls one whole row per wheel notch. A standard Tk menu cannot do this, since it shows every entry in one font and never scrolls, so the list is a small borderless window that closes on a choice, Escape, a second click on the button or a click elsewhere. (The first version showed ten buttons in a grid; the owner preferred a scrollable list after the manual check.)

### Settings are stored in config.yaml under `settings`
A new `Settings` dataclass in `blocky/settings.py` holds `theme` (one of the five names or `follow-windows`), `dark_theme`, `light_theme`, `font` and `text_size`. Loading checks each field on its own and replaces a missing or unknown value with its default; the settings section never raises `DamagedConfig`, so a typo in the settings cannot make Blocky set the whole config aside. `Config` gains a `settings` field; config files without it load with the defaults.

Alternative considered: a separate settings file. Rejected: a second file to write safely, recover and back up, for five values.

### Follow Windows reads the registry and polls
Windows' app mode is the `AppsUseLightTheme` value under `HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize`. The window checks it every 2 seconds with Tk's `after` while Follow Windows is chosen, and redraws only when the mode has changed. If the value cannot be read, dark is assumed. `effective_theme(settings, windows_is_light)` is a pure function, so the choice of theme is tested without the registry.

Alternative considered: listening for the `WM_SETTINGCHANGE` message. Rejected: Tk does not pass that message to Python without a native window hook; a two-second registry read is cheap and simple.

### The block page builds its CSS from the theme table
`server.py` turns the page's fixed colours into CSS variables filled from the effective theme, with the chosen font family and a root font size scaled by the text size. The server asks the app's settings through the same `load_state` path it uses for the block list, so the page follows changes on its next load. The favicon link carries the theme name (`/favicon.ico?theme=aqua`) so Brave does not keep showing the previous theme's icon from its cache.

Colour mapping on the page: page background `BACKGROUND`, main card `CARD` with a top stripe in `DEEP`, the name Blocky in `ACCENT` next to the theme's icon (served from the same per-theme icon as the favicon), the heading in `TEXT` with the domain in bold and the end time as a chip (`DEEP` fill, `ON_DEEP` text, like the blocked-site chips on the Status tab), the lead line in `MUTED`, and each suggestion in a `BACKGROUND` row with a left edge in `ACCENT`. There is no countdown: a ticking clock on a page meant to send the user elsewhere draws attention back to the blocked site, and the end time does not go stale.

### One icon per theme
`tools/make_icons.py` draws the icon for each theme: a rounded square in the theme's `PRIMARY` colour (`DEEP` for Forest, as today) with the "B" in `ON_PRIMARY` (`ACCENT` for Forest), written to `blocky/assets/blocky-<theme>.ico`. `blocky.ico` and the extension PNGs stay the Forest icon. The light themes use the button colour rather than the paler status-card colour so the icon still stands out at 16 pixels.

### Tests
- Contrast: for every theme and every (text, surface) pair the window uses, the WCAG ratio meets 4.5 (3 for borders and disabled buttons). This guards every future colour edit.
- Settings: defaults; a round trip through config.yaml; every field missing, of the wrong type or unknown falls back on its own; reset changes only the settings; property test that any YAML value in the settings section loads without an error.
- Effective theme: every combination of choice, dark and light theme, and Windows mode.
- Window: each setting changes the window and survives a restart; a redraw keeps the selected tab; no widget keeps a colour from the previous theme; the window icon matches the theme.
- Block page: each theme's colours, the font and the size appear in the CSS, and the favicon matches the theme.
- Mutation testing on `settings.py` and the theme functions.

## Risks / Trade-offs

- [A redraw takes a moment and the window can flicker] → it only happens on a settings change; measured in the window test and acceptable below about half a second.
- [A colour default is missed and keeps the old theme] → the widget-walk test fails on any leftover colour.
- [Bahnschrift and Segoe UI Variable are missing on older Windows] → Tk falls back to its default font; Blocky targets Windows 11, where all ten are present.
- [Larger text clips in fixed-width controls] → fixed sizes scale with the text size, and the window test opens every tab at Extra large.
- [The pale Blossom icon fades into a light taskbar] → the dark letter stays visible; a darker outline can be added if it looks weak in use.

## Migration Plan

Existing config.yaml files have no `settings` section and load with the defaults, which equal today's look. No data is converted. Rolling back to an older Blocky ignores the `settings` section when reading, but an older version saving the config drops it, which only resets the look.
