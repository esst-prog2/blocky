## ADDED Requirements

### Requirement: Domain entry is guarded while typing
The system SHALL let a domain box hold only letters, digits, `-` and `.`, ignoring any other keystroke, and SHALL reduce a pasted web address to its domain when it is pasted. Under the add box the system SHALL show what will be added, or why the entry cannot be added, and SHALL only add the entry when it is a valid domain that is not on the list yet.

#### Scenario: Impossible characters ignored
- **WHEN** the user types `red dit!.com` into the add box
- **THEN** the box shows `reddit.com`

#### Scenario: Incomplete domain
- **WHEN** the add box holds `reddit`
- **THEN** the line under it reads "Not a full domain yet, e.g. reddit.com" and Add does nothing

#### Scenario: Valid new domain
- **WHEN** the add box holds `reddit.com` and it is not on the list
- **THEN** the line under it reads "Adds reddit.com and www.reddit.com" and Add adds it

#### Scenario: Domain already listed
- **WHEN** the add box holds `reddit.com` and it is already on the list
- **THEN** the line under it reads "reddit.com is already in the list" and Add does nothing

#### Scenario: Address pasted
- **WHEN** the user pastes `https://www.reddit.com/r/all?sort=new` into the add box
- **THEN** the box shows `www.reddit.com`
