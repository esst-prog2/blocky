import pytest

from blocky.suggestions import MAX_LENGTH, can_save_edit, check, hint


def test_spaces_are_tidied():
    assert check("  10-minute   walk ", []) == "10-minute walk"


@pytest.mark.parametrize(
    "text, message",
    [
        ("", "Type a suggestion"),
        ("   ", "Type a suggestion"),
        ("x" * (MAX_LENGTH + 1), "Keep it to 120 characters"),
    ],
)
def test_empty_or_long_suggestions_are_refused(text, message):
    with pytest.raises(ValueError, match=message):
        check(text, [])


def test_a_suggestion_of_the_maximum_length_is_accepted():
    assert check("x" * MAX_LENGTH, []) == "x" * MAX_LENGTH


def test_duplicates_are_refused_ignoring_case():
    with pytest.raises(ValueError, match="already in the list"):
        check("10-Minute Walk", ["10-minute walk"])


def test_a_suggestion_may_keep_its_own_text_when_edited():
    assert check("Walk", ["Walk", "Read"], original="Walk") == "Walk"


def test_hint_is_blank_for_an_empty_or_valid_box():
    assert hint("", []) == (False, "")
    assert hint("Walk", []) == (True, "")


def test_hint_explains_a_duplicate():
    assert hint("walk", ["Walk"]) == (False, "\u201cwalk\u201d is already in the list")


@pytest.mark.parametrize(
    "text, expected", [("Walk", False), (" Walk ", False), ("Read", False), ("Run", True), ("Yoga", True), ("", False)]
)
def test_edit_can_only_be_saved_when_valid_and_changed(text, expected):
    assert can_save_edit(text, "Walk", ["Walk", "Read"]) is expected
