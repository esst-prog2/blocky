"""English as it was before languages existed: every shown text, pinned, so translating cannot change it."""

import json
from pathlib import Path

import pytest
from shown_texts import SAMPLE_SETTINGS, open_sample, sample_pages, window_texts

ENGLISH = json.loads(Path(__file__).with_name("english_texts.json").read_text(encoding="utf-8"))
# The one addition since the pin: the Language row, first in the Language and time section.
LANGUAGE_ROW = ["Language", "Follow Windows  ▾", "Windows uses English."]


def with_language_row(texts: list[str]) -> list[str]:
    at = texts.index("Language and time") + 1
    return [*texts[:at], *LANGUAGE_ROW, *texts[at:]]


@pytest.mark.parametrize("number", range(len(SAMPLE_SETTINGS)))
def test_window_shows_the_pinned_english(tmp_path, open_app, number):
    app = open_sample(open_app, tmp_path, SAMPLE_SETTINGS[number])
    try:
        assert window_texts(app) == with_language_row(ENGLISH["window"][number])
    finally:
        app.destroy()


@pytest.mark.parametrize("twelve_hour", [False, True])
def test_block_page_shows_the_pinned_english(twelve_hour):
    pages = sample_pages({"timeStyle": {"twelveHour": twelve_hour, "firstDay": 0}})
    assert pages == ENGLISH["pages"]["12h" if twelve_hour else "24h"]
