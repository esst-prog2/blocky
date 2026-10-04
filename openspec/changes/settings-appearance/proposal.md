## Why

Blocky has one fixed dark look, with one font and one text size. Some people work better with a light screen, others need larger text, and the block page in Brave should look like the app it belongs to. This is the first of four parts of a Settings feature (appearance; time format and first day of week; languages; start with Windows), and it lays the groundwork the other three build on: the Settings tab, stored settings, and a window that redraws itself when a setting changes.

## What Changes

- A new **Settings** tab, after Shortlist, where every change takes effect immediately and is saved; there is no Save button.
- **Theme**: five themes, two dark and three light, plus **Follow Windows**, which uses a chosen dark and a chosen light theme to match Windows' own light or dark mode.
  - Forest (dark): the current theme, unchanged.
  - Navy (dark): based on 27374D / 526D82 / 9DB2BF / DDE6ED.
  - Sand (light): based on AD8B73 / CEAB93 / E3CAA5 / FFFBE9, with a terracotta button.
  - Aqua (light): based on E3FDFD / CBF1F5 / A6E3E9 / 71C9CE.
  - Blossom (light): based on F9F5F6 / F8E8EE / FDCEDF / F2BED1.
  Every text colour in every theme stays readable (WCAG AA, 4.5:1; borders and disabled buttons 3:1).
- **Font**: ten fonts that come with Windows: Segoe UI Variable (default), Segoe UI, Bahnschrift, Calibri, Candara, Corbel, Verdana, Tahoma, Georgia and Constantia.
- **Text size**: Small, Normal (default), Large and Extra large (90, 100, 115 and 130 %).
- **Reset to default** puts all settings back to Forest, Segoe UI Variable and Normal, without touching sites, schedule, suggestions or history.
- The **block page** follows the theme, font and text size.
- The **icon** follows the theme in the window, the taskbar and the block page's browser tab. The Start-menu shortcut and the extension keep the Forest icon.

## Capabilities

### New Capabilities
- `settings`: the Settings tab, the stored settings with their defaults, the themes and Follow Windows, fonts, text sizes, reset to default, and the theme-dependent window icon.

### Modified Capabilities
- `block-page`: the block page follows the chosen theme, font and text size, and its browser-tab icon follows the theme.

## Impact

- `blocky/theme.py`: colours and fonts become the current theme's values, switchable at runtime; the five themes are defined here.
- New `blocky/settings.py`: the settings, their defaults, and checking stored values.
- `blocky/config.py`: a `settings` section in config.yaml; a missing or damaged section falls back to the defaults.
- `blocky/app.py`: the Settings tab, and rebuilding the window when a setting changes.
- `blocky/server.py`: the block page's colours, font, size and favicon come from the settings.
- `tools/make_icons.py`, `blocky/assets/`: one icon per theme.
- Tests: new settings, theme and window tests; block page tests for each theme.
- Out of scope: the shortcut and extension icons; time format, first day of week, languages and start with Windows (parts 2 to 4).
