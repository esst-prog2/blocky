import pytest

from blocky import hosts

ORIGINAL = "127.0.0.1 localhost\n10.0.0.5 printer.local\n"


def test_adds_blocky_section_and_keeps_other_lines():
    result = hosts.render(ORIGINAL, ["reddit.com", "www.reddit.com"])
    assert result == (
        "127.0.0.1 localhost\n"
        "10.0.0.5 printer.local\n"
        "# BEGIN BLOCKY\n"
        "127.0.0.1 reddit.com\n"
        "127.0.0.1 www.reddit.com\n"
        "# END BLOCKY\n"
    )


def test_empty_list_removes_section_and_keeps_other_lines():
    with_section = hosts.render(ORIGINAL, ["reddit.com"])
    assert hosts.render(with_section, []) == ORIGINAL


def test_rendering_twice_is_idempotent():
    once = hosts.render(ORIGINAL, ["reddit.com"])
    assert hosts.render(once, ["reddit.com"]) == once


def test_crlf_line_endings_are_preserved():
    text = "127.0.0.1 localhost\r\n"
    assert hosts.render(text, ["reddit.com"]).count("\r\n") == 4


def test_unterminated_section_is_rejected_without_changes():
    broken = "# BEGIN BLOCKY\n127.0.0.1 reddit.com\n"
    with pytest.raises(ValueError):
        hosts.render(broken, [])


def test_apply_writes_only_when_changed(tmp_path):
    path = tmp_path / "hosts"
    path.write_text(ORIGINAL, encoding="utf-8")
    assert hosts.apply(["reddit.com"], path) is True
    assert hosts.apply(["reddit.com"], path) is False
    assert "127.0.0.1 reddit.com" in path.read_text(encoding="utf-8")


def test_apply_creates_missing_file(tmp_path):
    path = tmp_path / "hosts"
    assert hosts.apply(["reddit.com"], path) is True
    assert path.read_text(encoding="utf-8").startswith("# BEGIN BLOCKY")
