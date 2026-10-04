"""The user's appearance settings, their defaults, and how stored values are checked."""

from dataclasses import asdict, dataclass, replace

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

PERSONALIZE_KEY = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"


@dataclass(frozen=True)
class Settings:
    theme: str = "forest"
    dark_theme: str = "forest"
    light_theme: str = "sand"
    font: str = "Segoe UI Variable"
    text_size: str = "normal"


CHOICES = {
    "theme": (*THEMES, FOLLOW_WINDOWS),
    "dark_theme": DARK_THEMES,
    "light_theme": LIGHT_THEMES,
    "font": FONTS,
    "text_size": tuple(TEXT_SIZES),
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
