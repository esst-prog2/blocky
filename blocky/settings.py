"""The user's settings, their defaults, and how stored values are checked."""

from dataclasses import asdict, dataclass, replace

from blocky.clock import TimeStyle
from blocky.language import LANGUAGES, marked

DARK_THEMES = ("forest", "navy")
LIGHT_THEMES = ("sand", "aqua", "blossom")
THEMES = DARK_THEMES + LIGHT_THEMES
FOLLOW_WINDOWS = "follow-windows"
FONTS = (
    "Segoe UI Variable",
    "Segoe UI",
    "Bahnschrift",
    "Calibri",
    "Candara",
    "Corbel",
    "Verdana",
    "Tahoma",
    "Georgia",
    "Constantia",
)
TEXT_SIZES = {"small": 0.9, "normal": 1.0, "large": 1.15, "extra-large": 1.3}
TIME_FORMATS = ("24h", "12h")
FIRST_DAYS = {"monday": 0, "saturday": 5, "sunday": 6}  # the first days used around the world

# Theme and text size names as shown, in English; the window shows them translated.
NAMES = {
    "forest": marked("Forest"),
    "navy": marked("Navy"),
    "sand": marked("Sand"),
    "aqua": marked("Aqua"),
    "blossom": marked("Blossom"),
    "small": marked("Small"),
    "normal": marked("Normal"),
    "large": marked("Large"),
    "extra-large": marked("Extra large"),
}

PERSONALIZE_KEY = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
INTERNATIONAL_KEY = r"Control Panel\International"


@dataclass(frozen=True)
class Settings:
    theme: str = "forest"
    dark_theme: str = "forest"
    light_theme: str = "sand"
    font: str = "Segoe UI Variable"
    text_size: str = "normal"
    time_format: str = FOLLOW_WINDOWS
    first_day: str = FOLLOW_WINDOWS
    language: str = FOLLOW_WINDOWS


CHOICES = {
    "theme": (*THEMES, FOLLOW_WINDOWS),
    "dark_theme": DARK_THEMES,
    "light_theme": LIGHT_THEMES,
    "font": FONTS,
    "text_size": tuple(TEXT_SIZES),
    "time_format": (FOLLOW_WINDOWS, *TIME_FORMATS),
    "first_day": (FOLLOW_WINDOWS, *FIRST_DAYS),
    "language": (FOLLOW_WINDOWS, *LANGUAGES),
}


def label(name: str) -> str:
    """How a theme or text size is shown: 'extra-large' becomes 'Extra large'."""
    return name.replace("-", " ").capitalize()


def from_data(data: object) -> Settings:
    """Settings from the config's `settings` section; each missing or unknown value falls back to its default."""
    if not isinstance(data, dict):
        return Settings()
    values = {key: data[key] for key, choices in CHOICES.items() if key in data and data[key] in choices}
    return replace(Settings(), **values)


def to_data(settings: Settings) -> dict:
    return asdict(settings)


def effective_theme(settings: Settings, windows_is_light: bool) -> str:
    """The theme the window shows: the chosen one, or under Follow Windows the dark or light choice."""
    if settings.theme != FOLLOW_WINDOWS:
        return settings.theme
    return settings.light_theme if windows_is_light else settings.dark_theme


def windows_is_light() -> bool:
    """Whether Windows apps are set to light mode; dark when the setting cannot be read."""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PERSONALIZE_KEY) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
    except (ImportError, OSError):
        return False
    return value == 1


@dataclass(frozen=True)
class WindowsTime:
    """Windows' own regional choices: 12-hour clock, and the first day of the week (0 Monday to 6 Sunday)."""

    twelve_hour: bool = False
    first_day: int = 0


def _international(name: str) -> str | None:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNATIONAL_KEY) as key:
            value, _ = winreg.QueryValueEx(key, name)
    except (ImportError, OSError):
        return None
    return value if isinstance(value, str) else None


def windows_time() -> WindowsTime:
    """Windows' short time format and first day of the week; 24-hour and Monday for what cannot be read."""
    short_time = _international("sShortTime") or ""
    first_day = _international("iFirstDayOfWeek") or ""
    return WindowsTime(
        twelve_hour="h" in short_time and "H" not in short_time,
        first_day=int(first_day) if first_day.isascii() and first_day.isdigit() and int(first_day) < 7 else 0,
    )


def time_style(settings: Settings, windows: WindowsTime, language: str = "en") -> TimeStyle:
    """The time format and first day the window uses: the chosen ones, or Windows' under Follow Windows.

    `language` is the effective language, which sets the day and month names and the AM/PM markers.
    """
    twelve_hour = windows.twelve_hour if settings.time_format == FOLLOW_WINDOWS else settings.time_format == "12h"
    first_day = windows.first_day if settings.first_day == FOLLOW_WINDOWS else FIRST_DAYS[settings.first_day]
    return TimeStyle(twelve_hour=twelve_hour, first_day=first_day, language=language)


def effective_language(settings: Settings, windows: str) -> str:
    """The language Blocky writes in: the chosen one, or under Follow Windows Windows' display language.

    English when Windows uses a language Blocky does not have.
    """
    chosen = windows if settings.language == FOLLOW_WINDOWS else settings.language
    return chosen if chosen in LANGUAGES else "en"
