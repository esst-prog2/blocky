## ADDED Requirements

### Requirement: Edited domain is saved only when valid and changed
The system SHALL allow saving an edited block-list entry only when it is a valid domain, differs from the saved entry, and is not another entry on the list.

#### Scenario: Valid change
- **WHEN** the user edits `chess.com` to `lichess.org`
- **THEN** Save is available and saves `lichess.org`

#### Scenario: Incomplete, unchanged or duplicate edit
- **WHEN** the user edits `chess.com` to `chess`, leaves it as `chess.com`, or edits it to `reddit.com` while `reddit.com` is on the list
- **THEN** Save is disabled
