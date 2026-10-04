import pytest

from blocky.timefield import TimeField, allowed, finish, step


@pytest.mark.parametrize("text", ["", "0", "9", "09", "23"])
def test_hour_box_allows_valid_typing(text):
    assert allowed(text, 23)


@pytest.mark.parametrize("text", ["24", "99", "a", "1a", "123", "-1", " 9"])
def test_hour_box_ignores_invalid_typing(text):
    assert not allowed(text, 23)


def test_minute_box_allows_up_to_59():
    assert allowed("59", 59)
    assert not allowed("60", 59)


@pytest.mark.parametrize(
    "text, delta, maximum, result",
    [
        ("09", 1, 23, "10"),
        ("23", 1, 23, "00"),
        ("00", -1, 23, "23"),
        ("59", 1, 59, "00"),
        ("", 1, 59, "01"),
    ],
)
def test_stepping_wraps_around(text, delta, maximum, result):
    assert step(text, delta, maximum) == result


def test_leaving_a_box_pads_a_single_digit():
    assert finish("9", "17") == "09"


def test_leaving_a_box_empty_puts_back_the_previous_value():
    assert finish("", "17") == "17"


def test_a_box_holds_at_most_two_digits():
    assert not allowed("012", 59)


@pytest.fixture
def field(tk_root):
    time_field = TimeField(tk_root, "09:30")
    time_field.pack()
    tk_root.update()
    return time_field


def press(box, event, **details):
    # CTkEntry binds on the Tk entry inside it, and Tk only delivers key events to the focused widget.
    box._entry.focus_force()
    box.update()
    box._entry.event_generate(event, **details)


def test_field_shows_the_saved_time(field):
    assert field.hour.get() == "09"
    assert field.minute.get() == "30"
    assert field.get() == "09:30"


def test_arrow_keys_step_a_box_up_and_down(field):
    press(field.hour, "<Up>")
    assert field.hour.get() == "10"
    press(field.hour, "<Down>")
    press(field.hour, "<Down>")
    assert field.hour.get() == "08"


def test_mouse_wheel_steps_a_box(field):
    press(field.minute, "<MouseWheel>", delta=120)
    assert field.minute.get() == "31"
    press(field.minute, "<MouseWheel>", delta=-120)
    press(field.minute, "<MouseWheel>", delta=-120)
    assert field.minute.get() == "29"


def test_hours_wrap_after_23_and_minutes_after_59(field):
    field.hour._set("23")
    press(field.hour, "<Up>")
    field.minute._set("59")
    press(field.minute, "<Up>")
    assert field.get() == "00:00"
    press(field.hour, "<Down>")
    press(field.minute, "<Down>")
    assert field.get() == "23:59"


def test_typing_is_checked_against_each_box_maximum(field):
    field.hour.delete(0, "end")
    field.hour.insert(0, "24")
    field.minute.delete(0, "end")
    field.minute.insert(0, "60")
    assert field.hour.get() == ""
    assert field.minute.get() == ""
