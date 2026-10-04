## ADDED Requirements

### Requirement: Block page has a readable address
The system SHALL serve the block page at `http://blocky.localhost/<domain>`, without a port number when port 80 on this machine is free, and at `http://blocky.localhost:8765/<domain>` when it is not. The server SHALL only accept connections from this machine on both ports. A request for the earlier address `/blocked?domain=<domain>` SHALL be sent on to the new address.

#### Scenario: Port 80 free
- **WHEN** `reddit.com` is blocked, port 80 is free when Blocky starts, and the user opens reddit.com in Brave
- **THEN** the address bar shows `blocky.localhost/reddit.com`

#### Scenario: Port 80 taken
- **WHEN** another program uses port 80 when Blocky starts and the user opens a blocked site in Brave
- **THEN** the block page opens at `blocky.localhost:8765/<domain>`

#### Scenario: Earlier address
- **WHEN** a browser asks for `/blocked?domain=reddit.com`
- **THEN** it is sent on to `blocky.localhost/reddit.com` (or the port 8765 address when port 80 is taken)
