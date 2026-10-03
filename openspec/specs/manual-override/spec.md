# manual-override Specification

## Purpose
Gives the user a deliberate way to unblock a domain during an active window, with a required reason, so that exceptions are conscious and recorded.

## Requirements

### Requirement: Override requires a reason
The system SHALL unblock a currently blocked domain only when the user selects it and enters a non-empty reason. Until a reason is typed, the system SHALL keep the override action unavailable and prompt for a reason.

#### Scenario: Override with reason
- **WHEN** the user selects `reddit.com` while it is blocked, types "checking a work thread", and confirms
- **THEN** `reddit.com` is unblocked

#### Scenario: Override without reason
- **WHEN** a domain can be overridden and the reason is empty or only spaces
- **THEN** the Override button is disabled, "Type a reason to override" is shown, and the domain stays blocked

### Requirement: Override lasts until the current block window ends
The system SHALL keep an overridden domain unblocked until the end of the current scheduled block window, and SHALL re-block it at the start of the next window.

#### Scenario: Override expires with the window
- **WHEN** the user overrides `reddit.com` at 14:00 during a window ending at 17:00
- **THEN** `reddit.com` remains unblocked until 17:00 and is blocked again when the next window starts

### Requirement: Override is logged
The system SHALL record each override with the domain, the timestamp, and the reason.

#### Scenario: Override recorded
- **WHEN** an override is confirmed
- **THEN** the history log gains an entry containing the domain, timestamp, and reason

### Requirement: Override can be undone
The system SHALL let the user undo an active override, which re-blocks the domain at once, and SHALL keep the override's history line while adding a separate line stating the override was undone.

#### Scenario: Undo re-blocks the domain
- **WHEN** the user undoes the override of `reddit.com` at 14:30
- **THEN** `reddit.com` is blocked again immediately

#### Scenario: Undo is recorded without removing the override
- **WHEN** the user undoes an override
- **THEN** the history log keeps the override entry and gains a line stating that the override was undone
