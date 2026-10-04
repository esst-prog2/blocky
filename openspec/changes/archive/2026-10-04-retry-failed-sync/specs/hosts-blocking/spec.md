## MODIFIED Requirements

### Requirement: Background check runs about once a minute
The system SHALL compare the current time against the schedule and update the hosts file roughly once per minute while the app is running. When an update fails, the system SHALL try again after about 5 seconds instead of waiting the full minute.

#### Scenario: Window opens without user action
- **WHEN** the app is running and the scheduled start time passes
- **THEN** the hosts file is updated within about one minute, without the user doing anything

#### Scenario: Failed update is retried soon
- **WHEN** an update of the hosts file fails because the file is briefly locked
- **THEN** the system tries again after about 5 seconds, and the hosts file is updated once the lock is gone
