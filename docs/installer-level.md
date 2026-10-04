# Installer level: what waits for it

Blocky has no installer yet: it runs from the project folder through a Start-menu shortcut and asks UAC on every start. Several things were moved to a later installer level because an installer runs as administrator once, puts Blocky in a fixed folder, and can set things up that Blocky itself cannot do safely. This page collects them so none is forgotten. The decisions themselves, with their dates, are in `PLANNING_LOG.md`.

## 1. Install into C:\Program Files

- A fixed install folder that only administrators can change (decided 2026-10-04).
- It closes the security gap of a scheduled task with highest privileges (item 2): with Blocky in a user-writable folder, any program running as the user could change Blocky's files and have them run as administrator without a prompt.
- With a fixed folder, the planned repair of the task's path when the project moves is no longer needed.

## 2. Start without UAC prompts, and start with Windows (the former Settings part 4)

As planned on 2026-10-04, now to be set up by the installer:

- One scheduled task with highest privileges serves both starting from the shortcut and the optional start at login.
- At login Blocky starts minimised to the taskbar.
- The task may run on battery and has no time limit.
- Start with Windows is on after installing and can be switched off in Settings; whether it is on is read from Windows (the task), not stored in config.yaml.
- The Settings tab gets a Startup section for it (the layout already leaves room after Language and time). Reset to default leaves Start with Windows alone and says so.
- Until then Blocky asks UAC on each start and does not start with Windows.

## 3. Remove leftover blocking at boot

Found in spike p1-lifecycle (2026-10-04, `spike/p1-lifecycle/results.md`):

- When Windows restarts or shuts down with Blocky open, or Blocky is ended by force or crashes, or the power goes, Blocky's entries stay in the hosts file. They keep blocking, also after the window has ended, until Blocky starts again; then it removes them within about 30 seconds.
- Blocky itself cannot fix this. It now handles Windows' end-of-session notice (WM_SAVE_YOURSELF) and removes its entries when it gets it, which works when the notice is sent to its window, but at real restarts on 2026-10-04 the cleanup never ran: Windows did not deliver the notice in time, or ended Blocky first (possibly because it runs as administrator; not investigated further). It can never help when Blocky is killed or loses power. **So the installer's boot-time cleanup is the real fix.**
- **The installer's part:** a task that runs at boot as SYSTEM (before anyone logs in) and removes the lines between `# BEGIN BLOCKY` and `# END BLOCKY` when no block window is active, or simply starts Blocky's own background check. That covers crashes and power loss too. Combined with start with Windows (item 2), the leftovers are gone at the latest when the user logs in.
- Check it with the p1-lifecycle checklist cases 6 and 7b; they should then pass without starting Blocky by hand.
- If the reason Windows skips Blocky's cleanup matters later: a small probe that logs the shutdown notices it receives, run once normally and once as administrator during a restart, would show whether elevation is the cause.

## 4. Guard against running Blocky twice

- Not guarded now; it stays rare while Blocky does not start by itself (decided 2026-10-04).
- Once Blocky starts with Windows (item 2), starting it from the shortcut as well becomes likely. Two Blockys would both run a background check and a block page server (the second one finds port 8765 taken and shows a warning).
- An idea, not decided yet: a second start brings the running window to the front instead of starting again.

## 5. Smaller items

- The Start-menu shortcut and its icon (now made by `tools/create_shortcut.ps1`, with the Forest icon) become the installer's.
- The Python environment: the shortcut now runs the project's `.venv` `pythonw`; an installer needs its own Python or a frozen build.
- The browser extension is loaded from the project's `extension/` folder; the installer could put it in the fixed folder and explain how to load it in Brave.
