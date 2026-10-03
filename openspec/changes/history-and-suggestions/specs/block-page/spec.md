## ADDED Requirements

### Requirement: Suggestions are added and changed one at a time
The system SHALL let the user add one suggestion at a time through an add box that accepts only 1 to 120 characters that are not already on the list, ignoring case, and SHALL list the suggestions as rows that can each be edited, saved and removed. Add and Save SHALL only be available when the text is valid.

#### Scenario: Suggestion added
- **WHEN** the user types "10-minute walk" and presses Add
- **THEN** "10-minute walk" is added to the end of the shortlist

#### Scenario: Duplicate suggestion
- **WHEN** the shortlist contains "10-minute walk" and the user types "10-Minute Walk"
- **THEN** Add is disabled and the hint says it is already in the list

#### Scenario: Suggestion edited
- **WHEN** the user changes "Tidy desk" to "Tidy the desk" and saves
- **THEN** the shortlist holds "Tidy the desk" in the same place
