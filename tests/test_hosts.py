import os
import threading

import pytest

from blocky import files, hosts

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


BROKEN_SECTIONS = {
    "unterminated": "# BEGIN BLOCKY\n127.0.0.1 reddit.com\n",
    "nested": "# BEGIN BLOCKY\n# BEGIN BLOCKY\n# END BLOCKY\n",
    "end without start": "127.0.0.1 localhost\n# END BLOCKY\n",
}


@pytest.mark.parametrize("broken", BROKEN_SECTIONS.values(), ids=BROKEN_SECTIONS.keys())
def test_broken_section_is_rejected_without_changes(tmp_path, broken):
    path = tmp_path / "hosts"
    path.write_text(broken, encoding="utf-8")
    with pytest.raises(ValueError):
        hosts.apply(["reddit.com"], path)
    assert path.read_text(encoding="utf-8") == broken


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


def test_apply_retries_when_the_swap_is_briefly_locked(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    real_replace = os.replace
    failures = {"left": 3}

    def locked_replace(source, target):
        if failures["left"]:
            failures["left"] -= 1
            raise PermissionError(13, "Access is denied")
        real_replace(source, target)

    monkeypatch.setattr(files.os, "replace", locked_replace)
    monkeypatch.setattr(files, "REPLACE_DELAY", 0)

    assert hosts.apply(["reddit.com"], path)
    assert "127.0.0.1 reddit.com" in path.read_text(encoding="utf-8")
    assert not (tmp_path / "hosts.tmp").exists()


def test_apply_writes_in_place_when_the_swap_stays_locked(tmp_path, monkeypatch):
    path = tmp_path / "hosts"
    path.write_text(
        "127.0.0.1 localhost\n" + hosts.BEGIN + "\n127.0.0.1 reddit.com\n" + hosts.END + "\n", encoding="utf-8"
    )

    def always_locked(source, target):
        raise PermissionError(13, "Access is denied")

    monkeypatch.setattr(files.os, "replace", always_locked)
    monkeypatch.setattr(files, "REPLACE_DELAY", 0)

    assert hosts.apply([], path)
    assert path.read_text(encoding="utf-8") == "127.0.0.1 localhost\n"
    assert not (tmp_path / "hosts.tmp").exists()


def test_two_writers_at_once_do_not_collide(tmp_path):
    path = tmp_path / "hosts"
    path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    errors = []

    def write(hostnames):
        for turn in range(200):
            try:
                hosts.apply(hostnames if turn % 2 else [], path)
            except OSError as error:
                errors.append(error)

    writers = [threading.Thread(target=write, args=([name],)) for name in ("a.com", "b.com")]
    for writer in writers:
        writer.start()
    for writer in writers:
        writer.join()

    assert errors == []
    assert "127.0.0.1 localhost" in path.read_text(encoding="utf-8")
