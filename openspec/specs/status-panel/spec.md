# status-panel Specification

## Purpose
Shows the user at a glance which domains are blocked right now and how long until the next change, so the state of the system is never a mystery.

## Requirements

### Requirement: Status panel shows blocked domains and time remaining
The system SHALL display the currently blocked domains and the time remaining until the next change in blocking state.

#### Scenario: Blocking active
- **WHEN** the current time is inside an active window at 14:00 and the window ends at 17:00
- **THEN** the panel reads "Blocking active — 3h 00m remaining" and lists the blocked domains

#### Scenario: Domain overridden
- **WHEN** `reddit.com` is overridden until 17:00
- **THEN** the panel reads "reddit.com unblocked until 17:00" with a countdown

### Requirement: Status panel updates live
The system SHALL update the status panel at least once per minute without the user reopening the app.

#### Scenario: Countdown advances
- **WHEN** the app stays open across a minute boundary
- **THEN** the remaining time shown is reduced accordingly
