## Why

After the time and domain fields, two places still say "no" only after a click: Override with no reason shows a red error, and Save on an edited domain accepts an incomplete or duplicate entry and then shows an error. They should follow the same pattern as Add: the button only works when the action can succeed.

## What Changes

- The Override button is disabled until a domain can be overridden and a reason has been typed; while the reason is missing, "Type a reason to override" is shown. Enter in the reason box overrides. The Undo override button is disabled when nothing can be undone.
- Each Save button in the block list is disabled until the edited domain is valid, different from the saved one, and not another entry on the list.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `manual-override`: the scenario for a missing reason changes from an error after confirming to a disabled button with a prompt.
- `block-list`: a requirement for saving an edited domain is added.

## Impact

- `blocky/app.py`: button states for Override, Undo override and the edit Save buttons.
- `blocky/domainfield.py`: `can_save_edit`.
- `tests/test_app.py` and `tests/test_domainfield.py`.
