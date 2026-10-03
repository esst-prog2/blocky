## Purpose

Gives the user a deliberate way to unblock a domain during an active window, with a required reason, so that exceptions are conscious and recorded.

## ADDED Requirements

### Requirement: Override requires a reason
The system SHALL unblock a currently blocked domain only when the user selects it and enters a non-empty reason.

#### Scenario: Override with reason
- **WHEN** the user selects `reddit.com` while it is blocked, types "checking a work thread", and confirms
- **THEN** `reddit.com` is unblocked

#### Scenario: Override without reason
- **WHEN** the user confirms an override with an empty reason
- **THEN** the domain stays blocked and the app asks for a reason

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
