## ADDED Requirements

### Requirement: Pasted web address is reduced to its domain
The system SHALL accept a web address as a block-list entry by removing its scheme, port, path, query and fragment, and SHALL then check and store only the domain.

#### Scenario: Address pasted from the address bar
- **WHEN** the user enters `https://www.reddit.com/r/all?sort=new`
- **THEN** `www.reddit.com` is added to the block list

#### Scenario: Address that is not a valid domain
- **WHEN** the user enters `https://reddit/`
- **THEN** the entry is rejected with an error message
