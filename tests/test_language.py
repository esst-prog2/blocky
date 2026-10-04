import ctypes

import pytest

from blocky import language
from blocky.language import _, translate


@pytest.fixture(autouse=True)
def sample_tables(monkeypatch):
    monkeypatch.setitem(language.NL, "Add a site", "Site toevoegen")
    monkeypatch.setitem(language.NL, "{domain} is already in the list", "{domain} staat al in de lijst")
    monkeypatch.setitem(language.HU, "{domain} is blocked until {time}", "{domain} {time}-ig tiltva van")


def test_english_gives_the_text_unchanged():
    assert translate("Add a site", "en") == "Add a site"


def test_a_text_is_looked_up_in_the_language():
    assert translate("Add a site", "nl") == "Site toevoegen"


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("en", "reddit.com is already in the list"),
        ("nl", "reddit.com staat al in de lijst"),
        ("hu", "reddit.com már szerepel a listán"),
    ],
)
def test_placeholders_are_filled_in_every_language(code, expected):
    assert translate("{domain} is already in the list", code, domain="reddit.com") == expected


def test_placeholders_may_change_order():
    text = translate("{domain} is blocked until {time}", "hu", domain="reddit.com", time="17:00")
    assert text == "reddit.com 17:00-ig tiltva van"


def test_a_missing_entry_falls_back_to_english():
    assert translate("Not in any table", "nl") == "Not in any table"


def test_an_unknown_language_falls_back_to_english():
    assert translate("Add a site", "fr") == "Add a site"


def test_braces_are_kept_when_nothing_is_filled_in():
    assert translate("{not a placeholder}", "nl") == "{not a placeholder}"


def test_the_current_language_is_used_by_underscore():
    language.apply("nl")
    assert language.current() == "nl"
    assert _("Add a site") == "Site toevoegen"
    language.apply("en")
    assert _("Add a site") == "Add a site"


def test_an_unknown_code_makes_english_current():
    language.apply("nl")
    language.apply("fr")
    assert language.current() == "en"


def test_marked_returns_the_text_itself():
    assert language.marked("Site added") == "Site added"


@pytest.mark.parametrize(
    ("langid", "code"),
    [
        (0x0413, "nl"),  # nl-NL
        (0x0813, "nl"),  # nl-BE
        (0x040E, "hu"),  # hu-HU
        (0x0409, "en"),  # en-US
        (0x0809, "en"),  # en-GB
        (0x040C, "other"),  # fr-FR: not offered
        (0x0000, "other"),
    ],
)
def test_windows_langids_map_to_a_language(langid, code):
    assert language.from_langid(langid) == code


def test_windows_language_reads_the_display_language(monkeypatch):
    monkeypatch.setattr(ctypes.windll.kernel32, "GetUserDefaultUILanguage", lambda: 0x040E)
    assert language.windows_language() == "hu"


def test_windows_language_is_english_when_it_cannot_be_read(monkeypatch):
    def fail():
        raise OSError("not available")

    monkeypatch.setattr(ctypes.windll.kernel32, "GetUserDefaultUILanguage", fail)
    assert language.windows_language() == "en"


def test_windows_language_is_english_without_windll(monkeypatch):
    monkeypatch.delattr(ctypes, "windll")
    assert language.windows_language() == "en"


def test_shown_text_keeps_its_english(monkeypatch):
    monkeypatch.setitem(language.NL, "it is not valid YAML", "het is geen geldige YAML")
    monkeypatch.setitem(
        language.NL, "{name} could not be read ({problem})", "{name} kon niet gelezen worden ({problem})"
    )
    language.apply("nl")
    problem = language.shown("it is not valid YAML")
    message = language.shown("{name} could not be read ({problem})", name="config.yaml", problem=problem)
    assert message == "config.yaml kon niet gelezen worden (het is geen geldige YAML)"
    assert language.english(message) == "config.yaml could not be read (it is not valid YAML)"


def test_english_of_a_plain_value_is_the_value():
    assert language.english("as it is") == "as it is"
    assert language.english(3) == 3


def test_a_context_picks_its_own_entry(monkeypatch):
    monkeypatch.setitem(language.NL, "Override", "Opheffen")
    monkeypatch.setitem(language.NL, "event|Override", "Blokkade opgeheven")
    assert translate("Override", "nl") == "Opheffen"
    assert translate("Override", "nl", context="event") == "Blokkade opgeheven"
    assert translate("Override", "en", context="event") == "Override"
    assert language.marked("Override", context="event") == "Override"
