# hosts-blocking Specification

## Purpose
Keeps the Windows hosts file in step with the block list and schedule, so that blocked domains resolve to the local machine only during active windows.

## Requirements

### Requirement: Blocked domains are redirected during active windows
The system SHALL write a `127.0.0.1` entry to the Windows hosts file for each block-list domain while the schedule is active and that domain is not overridden.

#### Scenario: Entry added when a window opens
- **WHEN** the current time enters an active schedule window for `reddit.com`
- **THEN** the hosts file contains a `127.0.0.1 reddit.com` entry and a `127.0.0.1 www.reddit.com` entry

### Requirement: Entries are removed outside the active window
The system SHALL remove the hosts-file entries for a domain when the schedule is inactive for that domain, including any leftover entries from before a schedule change.

#### Scenario: Entry removed when a window closes
- **WHEN** the current time leaves the active schedule window
- **THEN** the hosts file contains no entries for the block-list domains

#### Scenario: Leftover entry cleaned up
- **WHEN** the app starts and the hosts file contains a Blocky entry outside the active window
- **THEN** the entry is removed

### Requirement: Background check runs about once a minute
The system SHALL compare the current time against the schedule and update the hosts file roughly once per minute while the app is running. When an update fails, the system SHALL try again after about 5 seconds instead of waiting the full minute.

#### Scenario: Window opens without user action
- **WHEN** the app is running and the scheduled start time passes
- **THEN** the hosts file is updated within about one minute, without the user doing anything

#### Scenario: Failed update is retried soon
- **WHEN** an update of the hosts file fails because the file is briefly locked
- **THEN** the system tries again after about 5 seconds, and the hosts file is updated once the lock is gone

### Requirement: App runs elevated
The system SHALL run with administrator rights from startup so that writing the hosts file never triggers a UAC prompt during use.

#### Scenario: Write succeeds without prompt
- **WHEN** the schedule opens a block window while the app is running
- **THEN** the hosts file is written without a UAC prompt

### Requirement: Hosts file is written only from validated entries
The system SHALL write only domains that passed block-list validation and SHALL NOT modify hosts-file lines that Blocky did not create.

#### Scenario: Unrelated lines preserved
- **WHEN** the hosts file contains lines not created by Blocky
- **THEN** those lines remain unchanged after Blocky updates its entries
