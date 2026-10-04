"""Every text the code marks for translation has a Dutch and a Hungarian entry, and no entry is left unused."""

import ast
import string
from pathlib import Path

import pytest

from blocky import language

SOURCE = Path(__file__).parent.parent / "blocky"
MARKERS = ("_", "translate", "marked", "shown")


def marked_texts(source: str) -> set[str]:
    """The literal first argument of every call to _(), translate(), marked() or shown() in the source."""
    found = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
        if name in MARKERS and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            context = next((k.value for k in node.keywords if k.arg == "context"), None)
            if isinstance(context, ast.Constant) and isinstance(context.value, str) and context.value:
                found.add(f"{context.value}|{node.args[0].value}")  # the table key for a text with a context
            else:
                found.add(node.args[0].value)
    return found


def placeholders(text: str) -> set[str]:
    text = text.split("|", 1)[-1] if "|" in text else text  # a context is part of the key, not the text
    return {field for _, field, _, _ in string.Formatter().parse(text) if field is not None}


def problems(sources: list[str], tables: dict[str, dict[str, str]]) -> list[str]:
    texts = set().union(*(marked_texts(source) for source in sources))
    found = []
    for code, table in tables.items():
        for text in sorted(texts):
            if text not in table:
                found.append(f"{code}: no entry for {text!r}")
            elif placeholders(table[text]) != placeholders(text):
                found.append(f"{code}: other placeholders in {table[text]!r} than in {text!r}")
        found.extend(f"{code}: unused entry {text!r}" for text in sorted(set(table) - texts))
    return found


def test_every_marked_text_is_translated_and_no_entry_is_unused():
    sources = [path.read_text(encoding="utf-8") for path in sorted(SOURCE.glob("*.py"))]
    assert problems(sources, language.TABLES) == []


SAMPLE = 'from blocky.language import _, marked\n_("Add a site")\nlanguage.translate("Hi {name}", code)\nmarked("Site added")\nprint("not marked")\n'


def test_the_scan_finds_texts_in_each_kind_of_call():
    assert marked_texts(SAMPLE) == {"Add a site", "Hi {name}", "Site added"}


def test_the_scan_ignores_texts_that_are_not_literals():
    assert marked_texts("_(name)\n_(f'{x}')\nmarked(EVENTS[kind])\n") == set()


@pytest.mark.parametrize(
    ("table", "expected"),
    [
        ({"Add a site": "a", "Hi {name}": "Hoi {name}"}, ["nl: no entry for 'Site added'"]),
        (
            {"Add a site": "a", "Hi {name}": "Hoi {name}", "Site added": "b", "Gone": "c"},
            ["nl: unused entry 'Gone'"],
        ),
        (
            {"Add a site": "a", "Hi {name}": "Hoi {naam}", "Site added": "b"},
            ["nl: other placeholders in 'Hoi {naam}' than in 'Hi {name}'"],
        ),
        ({"Add a site": "a", "Hi {name}": "Hoi {name}", "Site added": "b"}, []),
    ],
)
def test_problems_names_missing_unused_and_mismatched_entries(table, expected):
    assert problems([SAMPLE], {"nl": table}) == expected
