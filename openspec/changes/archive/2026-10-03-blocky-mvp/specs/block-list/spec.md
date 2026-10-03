## Purpose

Lets the user maintain the set of domains that Blocky blocks, with validation so that malformed entries never reach the hosts file.

## ADDED Requirements

### Requirement: User can add, edit, and remove blocked domains
The system SHALL let the user add, edit, and remove blocked domains through a text input in the app.

#### Scenario: Adding a valid domain
- **WHEN** the user enters `reddit.com` and confirms
- **THEN** `reddit.com` appears in the block list

#### Scenario: Removing a domain
- **WHEN** the user removes `reddit.com` from the block list
- **THEN** `reddit.com` no longer appears in the block list

### Requirement: Each entry also blocks its www. variant
The system SHALL treat every block-list entry as covering both the entered hostname and its `www.` variant.

#### Scenario: www variant is covered
- **WHEN** the block list contains `youtube.com`
- **THEN** the system treats `www.youtube.com` as blocked as well

### Requirement: Malformed domains are rejected
The system SHALL reject any entry that is missing a dot, contains spaces, or is otherwise not a valid hostname, show an error message, and SHALL NOT add it to the block list or the hosts file.

#### Scenario: Entry without a dot
- **WHEN** the user enters `reddit`
- **THEN** the app shows an error message and the block list is unchanged

#### Scenario: Entry with spaces
- **WHEN** the user enters `red dit.com`
- **THEN** the app shows an error message and the block list is unchanged
