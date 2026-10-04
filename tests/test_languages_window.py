"""The window and block page in Dutch and Hungarian: nothing left in English, and the Language setting itself."""

from dataclasses import replace
from datetime import datetime

import pytest
from fit import cut_off, tabs_fit
from shown_texts import (
    MONDAY_2PM as MONDAY,
)
from shown_texts import (
    SAMPLE_OVERRIDES,
    SAMPLE_SETTINGS,
    open_sample,
    sample_config,
    sample_pages,
    window_texts,
)

from blocky import config as config_module
from blocky import language
from blocky import theme as t
from blocky.app import TABS
from blocky.settings import FOLLOW_WINDOWS, Settings

# Texts that are the same in every language: names, data and what the user typed.
SAME_EVERYWHERE = {
    "Blocky",
    ":",
    "example.com",
    "Segoe UI Variable  ▾",
    *language.NAMES.values(),
    "reddit.com",
    "x.com",
    "news.ycombinator.com",
    "youtube.com",
    "10-minute walk",
    "Tidy the desk",
    "Tidy desk",
    "twitter.com → x.com",
    *(entry["reason"] for entry in SAMPLE_OVERRIDES if "reason" in entry),
    "17:00",
    "lang=en",
}


def leftovers(english: list[str], translated: list[str], code: str) -> list[str]:
    """Texts shown the same as in English, apart from names and data, and translations that are the same on purpose."""
    assert len(translated) == len(english), "the window should have the same texts in every language"
    same_on_purpose = {text for text, translation in language.TABLES[code].items() if translation == text}
    same_on_purpose |= {text.upper() for text in same_on_purpose}  # History's column headers
    return [
        text
        for text, other in zip(english, translated, strict=True)
        if text == other and text not in SAME_EVERYWHERE and text not in same_on_purpose
    ]


@pytest.mark.parametrize("code", ["nl", "hu"])
@pytest.mark.parametrize("number", range(len(SAMPLE_SETTINGS)))
def test_no_english_is_left_in_the_window(tmp_path, open_app, code, number):
    english_app = open_sample(open_app, tmp_path / "en", SAMPLE_SETTINGS[number])
    english = window_texts(english_app)
    english_app.destroy()
    t.apply()
    app = open_sample(open_app, tmp_path / code, replace(SAMPLE_SETTINGS[number], language=code))
    try:
        assert leftovers(english, window_texts(app), code) == []
    finally:
        app.destroy()


@pytest.mark.parametrize("code", ["nl", "hu"])
@pytest.mark.parametrize("twelve_hour", [False, True])
def test_no_english_is_left_on_the_block_page(code, twelve_hour):
    style = {"timeStyle": {"twelveHour": twelve_hour, "firstDay": 0}}
    english = sample_pages(style)
    translated = sample_pages({**style, "language": code})
    for page, texts in english.items():
        found = leftovers(texts, translated[page], code)
        # The end time in 24-hour form is the same in every language.
        assert [text for text in found if not (text == "17:00" and not twelve_hour)] == [], page


# The Language setting in the window

SATURDAY = datetime(2026, 10, 10, 14, 0)


@pytest.fixture
def window(tmp_path, open_app):
    opened = []

    def open_window(settings=None, **kwargs):
        path = tmp_path / "config.yaml"
        if settings is not None:
            config_module.save(path, sample_config(settings))
        clock = kwargs.pop("clock", lambda: MONDAY)
        app = open_app(path, hosts_path=tmp_path / "hosts", clock=clock, **kwargs)
        app.update()
        opened.append(app)
        return app

    yield open_window
    for app in opened:
        try:
            app.destroy()
        except Exception:
            pass  # the test closed it already


def open_language_list(app):
    app.select_tab("Settings")
    app.update()
    app.language_list.button.invoke()
    app.update()
    return app.language_list.popup


def test_picking_dutch_shows_the_window_in_dutch_at_once_and_keeps_it(window, tmp_path):
    app = window(Settings())
    open_language_list(app)
    app.language_list.options["nl"].invoke()
    app.update()
    assert app.language_list.popup is None or not app.language_list.popup.winfo_exists()
    assert app.selected_tab == "Settings"
    assert app.tabs.get() == "Instellingen"
    assert app.list_title.cget("text") == "Geblokkeerde sites (3)"
    assert config_module.load(tmp_path / "config.yaml").settings.language == "nl"
    app.destroy()
    t.apply()
    again = window()
    assert again.tabs.get() == "Status"
    assert again.list_title.cget("text") == "Geblokkeerde sites (3)"


def test_language_list_names_each_language_in_itself(window):
    app = window(Settings(language="hu"))
    assert app.language_list.button.cget("text") == "Magyar  ▾"
    open_language_list(app)
    texts = [option.cget("text") for option in app.language_list.options.values()]
    assert texts == ["Windows szerint", "English", "Nederlands", "Magyar"]
    assert app.language_list.options["hu"].cget("fg_color") == t.DEEP  # the current one stands out


def test_language_list_shows_all_four_choices_without_scrolling(window):
    app = window(Settings(text_size="extra-large"))
    popup = open_language_list(app)
    canvas = app.language_list.scroll._parent_canvas
    top, bottom = canvas.winfo_rooty(), canvas.winfo_rooty() + canvas.winfo_height()
    for option in app.language_list.options.values():
        assert top - 1 <= option.winfo_rooty() and option.winfo_rooty() + option.winfo_height() <= bottom + 1
    assert not app.language_list.scroll._scrollbar.winfo_ismapped()
    assert popup.winfo_width() == app.language_list.button.winfo_width()
    assert app.language_list.button.cget("font").cget("family") == app.font_list.button.cget("font").cget("family")


def test_language_list_closes_like_the_font_list(window):
    app = window(Settings())
    popup = open_language_list(app)
    popup.event_generate("<Escape>")
    app.update()
    assert app.language_list.popup is None
    popup = open_language_list(app)
    popup.event_generate("<Button-1>", x=-50, y=-50)
    app.update()
    assert app.language_list.popup is None
    assert app.controller.config.settings.language == FOLLOW_WINDOWS


@pytest.mark.parametrize(
    "windows, tab, caption",
    [
        ("hu", "Beállítások", "A Windows nyelve magyar."),
        ("nl", "Instellingen", "Windows gebruikt Nederlands."),
        ("en", "Settings", "Windows uses English."),
        ("other", "Settings", "Windows uses another language, so Follow Windows gives English."),
    ],
)
def test_follow_windows_uses_windows_display_language(window, windows, tab, caption):
    app = window(Settings(), windows_language=lambda: windows)
    assert app.tab("Settings") is app.tabs.tab(tab)
    assert caption in window_texts(app)


def test_reset_puts_the_language_back_to_follow_windows_in_english(window, tmp_path):
    app = window(Settings(language="hu"))
    app.select_tab("Settings")
    app.reset_button.invoke()
    app.update()
    assert app.controller.config.settings.language == FOLLOW_WINDOWS
    assert app.tabs.get() == "Settings"
    assert app.reset_notice.winfo_children()[0].cget("text") == "Settings reset."
    assert app.undo_reset_button.cget("text") == "Undo"
    app.undo_reset_button.invoke()
    app.update()
    assert app.tabs.get() == "Beállítások"


def test_override_rows_keep_the_accent_colour_in_dutch(window):
    app = window(Settings(language="nl"))
    rows = [row.winfo_children() for row in app.history_list.winfo_children() if row.winfo_children()]
    colours = {cells[1].cget("text"): cells[1].cget("text_color") for cells in rows}
    assert colours["Blokkade opgeheven"] == t.ACCENT
    assert colours["Opheffing ongedaan gemaakt"] == t.ACCENT
    assert colours["Site toegevoegd"] == t.TEXT


def test_day_boxes_in_dutch(window):
    app = window(Settings(language="nl", first_day="monday"))
    assert [box.cget("text") for box in app.day_boxes.values()] == ["ma", "di", "wo", "do", "vr", "za", "zo"]


def test_status_in_hungarian_outside_the_block_window(window):
    app = window(Settings(language="hu"), clock=lambda: SATURDAY)
    assert app.status_label.cget("text") == "Most nincs tiltás"


def test_error_in_dutch(window):
    app = window(Settings(language="nl"))
    for box in app.day_boxes.values():
        box.deselect()
    app._save_schedule()
    assert app.schedule_message.cget("text") == "Kies minstens één dag"


def test_earlier_entries_follow_a_language_change(window):
    app = window(Settings(language="nl"))
    table = {row[1]: row for row in app.history_table()}
    assert table["Schema gewijzigd"][3] == "ma–vr, 09:00–17:00"
    assert table["Site toegevoegd"][0] == "zo 4 okt 2026, 17:05"


def test_status_lines_in_hungarian(window):
    app = window(Settings(language="hu"))
    assert app.status_label.cget("text") == "Tiltás aktív — még 3ó 00p"
    assert app.released_texts() == ["x.com feloldva eddig: 17:00 (még 3ó 00p)"]


@pytest.mark.parametrize(("code", "pm"), [("nl", "p.m."), ("hu", "du.")])
def test_twelve_hour_schedule_in_another_language(window, code, pm):
    app = window(Settings(language=code, time_format="12h"))
    assert app.end_time.period.cget("values") == [{"nl": "a.m.", "hu": "de."}[code], pm]
    assert app.end_time.period.get() == pm
    assert app.end_time.get() == "17:00"


# Layout: the longer Dutch and Hungarian texts still fit at Extra large in the smallest window


@pytest.mark.parametrize("font", ["Segoe UI Variable", "Verdana"])
@pytest.mark.parametrize("code", ["nl", "hu"])
@pytest.mark.parametrize("number", range(len(SAMPLE_SETTINGS)))
def test_every_text_fits_at_extra_large_in_the_smallest_window(window, code, font, number):
    settings = replace(SAMPLE_SETTINGS[number], language=code, text_size="extra-large", font=font)
    app = window(settings)
    app.geometry(f"{app._min_width}x{app._min_height}")
    app.update()
    assert tabs_fit(app)
    # History's table cells wrap within fixed columns, in English as well; they are left out here.
    table = {text for row in app.history_table() for text in row}
    table |= {language.translate(name, code).upper() for name, _width in app.HISTORY_COLUMNS}
    for tab in TABS:
        assert [text for text in cut_off(app, tab) if text not in table] == [], tab
