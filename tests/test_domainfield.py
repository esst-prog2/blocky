import tkinter

import pytest

from blocky.domainfield import MAX_LENGTH, DomainField, allowed, can_save_edit, cleaned_paste, hint


@pytest.mark.parametrize("text", ["", "reddit", "reddit.", "Reddit.com", "my-site.co.uk", "123.com"])
def test_domain_characters_are_allowed(text):
    assert allowed(text)


@pytest.mark.parametrize("text", ["red dit", "reddit!", "https://", "reddit.com/", "bücher.de", "a_b.com"])
def test_other_characters_are_refused(text):
    assert not allowed(text)


def test_overly_long_text_is_refused():
    assert not allowed("a" * 254)


def test_text_of_the_longest_possible_domain_is_allowed():
    assert MAX_LENGTH == 253
    assert allowed("a" * 253)


@pytest.mark.parametrize(
    "text, result",
    [
        ("https://www.reddit.com/r/all?sort=new", "www.reddit.com"),
        ("  Reddit.com  ", "reddit.com"),
        ("nos.nl:443", "nos.nl"),
        ("red dit.com", "reddit.com"),
    ],
)
def test_pastes_are_cleaned(text, result):
    assert cleaned_paste(text) == result


def test_hint_for_an_empty_box_is_blank():
    assert hint("", []) == (False, "")


def test_hint_for_an_incomplete_domain():
    assert hint("reddit", []) == (False, "Not a full domain yet, e.g. reddit.com")


def test_hint_for_a_new_domain():
    assert hint("reddit.com", []) == (True, "Adds reddit.com and www.reddit.com")


def test_hint_for_a_www_domain():
    assert hint("www.reddit.com", []) == (True, "Adds www.reddit.com")


def test_hint_for_a_domain_already_listed():
    assert hint("Reddit.com", ["reddit.com"]) == (False, "reddit.com is already in the list")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("chess.com", False),
        ("chess", False),
        ("reddit.com", False),
        ("apple.com", False),
        ("lichess.org", True),
        ("Chess.org", True),
        ("bbc.co.uk", True),
    ],
)
def test_edit_can_only_be_saved_when_valid_changed_and_not_a_duplicate(text, expected):
    # The list holds domains sorting both before and after the edited one.
    assert can_save_edit(text, "chess.com", ["apple.com", "reddit.com", "chess.com"]) is expected


@pytest.fixture
def box(tk_root):
    return DomainField(tk_root)


def test_paste_with_nothing_selected_inserts_the_domain(box):
    box.paste_text("https://nos.nl/artikel")
    assert box.get() == "nos.nl"


def test_paste_with_an_empty_clipboard_does_nothing(box, monkeypatch):
    def empty_clipboard():
        raise tkinter.TclError("CLIPBOARD selection doesn't exist")

    monkeypatch.setattr(box, "clipboard_get", empty_clipboard)
    assert box._paste(None) == "break"
    assert box.get() == ""
