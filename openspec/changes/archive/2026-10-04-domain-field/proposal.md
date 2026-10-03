## Why

A domain is typed as free text and only checked when Add is clicked, so the user finds out afterwards that it was wrong. Like the time fields, the box should keep out what can never be right and make clear before adding whether the entry is valid.

## What Changes

- Domain boxes accept only letters, digits, `-` and `.`; other keystrokes are ignored.
- A pasted web address is reduced to its domain the moment it is pasted.
- A line under the add box says what will be added ("Adds reddit.com and www.reddit.com"), or why it cannot be ("Not a full domain yet, e.g. reddit.com", "reddit.com is already in the list").
- Add, and Enter in the box, only work for a valid domain that is not on the list yet.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `block-list`: a requirement for guarded domain entry is added. The existing rejection of malformed domains stays as a second line of defence.

## Impact

- New `blocky/domainfield.py` with the typing, paste and hint rules and the `DomainField` box; `blocky/app.py` uses it for the add box and the edit boxes.
- `blocky/domains.py`: the address clean-up becomes public as `host_of`.
- New `tests/test_domainfield.py`; `tests/test_app.py` covers typing, pasting, the hint and the Add button.
