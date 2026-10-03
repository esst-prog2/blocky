import pytest

from blocky.timefield import allowed, finish, step


@pytest.mark.parametrize("text", ["", "0", "9", "09", "23"])
def test_hour_box_allows_valid_typing(text):
    assert allowed(text, 23)


@pytest.mark.parametrize("text", ["24", "99", "a", "1a", "123", "-1", " 9"])
def test_hour_box_ignores_invalid_typing(text):
    assert not allowed(text, 23)


def test_minute_box_allows_up_to_59():
    assert allowed("59", 59)
    assert not allowed("60", 59)


@pytest.mark.parametrize("text, delta, maximum, result", [
    ("09", 1, 23, "10"),
    ("23", 1, 23, "00"),
    ("00", -1, 23, "23"),
    ("59", 1, 59, "00"),
    ("", 1, 59, "01"),
])
def test_stepping_wraps_around(text, delta, maximum, result):
    assert step(text, delta, maximum) == result


def test_leaving_a_box_pads_a_single_digit():
    assert finish("9", "17") == "09"


def test_leaving_a_box_empty_puts_back_the_previous_value():
    assert finish("", "17") == "17"
