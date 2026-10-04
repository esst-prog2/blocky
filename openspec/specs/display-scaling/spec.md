# display-scaling Specification

## Purpose
Keeps Blocky's whole window, including its title bar, the right size on each monitor, so it does not look zoomed in or shrunk when it moves between screens with different scaling.

## Requirements

### Requirement: Window fits each monitor's scaling
The system SHALL show its window, including the title bar and window frame, at the scaling of the monitor the window is on, and SHALL adjust it when the window moves to a monitor with other scaling. This SHALL NOT change how the window resizes, maximises or restores.

#### Scenario: Window moved to an external monitor
- **WHEN** the window is moved from a laptop screen at 300 % to an external monitor with lower scaling
- **THEN** the title bar and the contents are shown at the external monitor's scaling

#### Scenario: Window moved back
- **WHEN** the window is moved back from the external monitor to the laptop screen
- **THEN** the title bar and the contents are shown at the laptop screen's scaling again

#### Scenario: Resizing on the external monitor
- **WHEN** the window is resized, maximised and restored on the external monitor
- **THEN** it takes the size the user chose and does not grow, shrink or move by itself

### Requirement: Startup does not depend on the scaling mode
If Windows does not allow the window to follow each monitor's scaling, the system SHALL start as before, with only the window contents following the monitor's scaling, and SHALL NOT show an error.

#### Scenario: Scaling mode refused
- **WHEN** Windows refuses the per-monitor scaling mode at startup
- **THEN** Blocky starts and works as it did before this change, without a warning
