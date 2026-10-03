## MODIFIED Requirements

### Requirement: Override requires a reason
The system SHALL unblock a currently blocked domain only when the user selects it and enters a non-empty reason. Until a reason is typed, the system SHALL keep the override action unavailable and prompt for a reason.

#### Scenario: Override with reason
- **WHEN** the user selects `reddit.com` while it is blocked, types "checking a work thread", and confirms
- **THEN** `reddit.com` is unblocked

#### Scenario: Override without reason
- **WHEN** a domain can be overridden and the reason is empty or only spaces
- **THEN** the Override button is disabled, "Type a reason to override" is shown, and the domain stays blocked
