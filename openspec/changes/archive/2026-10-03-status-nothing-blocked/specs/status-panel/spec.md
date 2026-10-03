## MODIFIED Requirements

### Requirement: Status panel shows blocked domains and time remaining
The system SHALL display the currently blocked domains and the time remaining until the next change in blocking state. During an active window in which no domain is blocked, because the block list is empty or every domain is overridden, the system SHALL say that nothing is blocked instead of that blocking is active.

#### Scenario: Blocking active
- **WHEN** the current time is inside an active window at 14:00 and the window ends at 17:00
- **THEN** the panel reads "Blocking active — 3h 00m remaining" and lists the blocked domains

#### Scenario: Domain overridden
- **WHEN** `reddit.com` is overridden until 17:00
- **THEN** the panel reads "reddit.com unblocked until 17:00" with a countdown

#### Scenario: Window active but nothing blocked
- **WHEN** the current time is inside an active window at 14:00 that ends at 17:00, and every domain on the list is overridden or the list is empty
- **THEN** the panel reads "Window active, nothing blocked — 3h 00m remaining"
