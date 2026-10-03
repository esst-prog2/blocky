## Context

See proposal.md for motivation and specs/ for requirements. The repository has no code yet, only the README and planning log. The app runs on Windows and must write the hosts file, which needs administrator rights. The browser is Brave (Chromium), so the extension uses Chrome's extension platform (Manifest V3).

## Goals / Non-Goals

**Goals:**
- One source of truth for the block list, schedule, and shortlist: the app.
- Blocking that does not depend on the browser's HTTP behavior.
- The extension holds no editable state of its own.

**Non-Goals:**
- Publishing the extension to a web store.
- Blocking that survives the app being closed beyond what is already in the hosts file.
- Remote hosting of the block page.

## Decisions

**Blocking through the hosts file, not a proxy.** Hosts-file entries are simple, need no network component, and match the README's stated mechanism. Alternative: a local proxy, rejected because it would also need to handle HTTPS certificates.

**The extension reacts to failed navigations and replaces the new-tab page.** Preloaded HTTPS sites never send plain HTTP, so an HTTP-only block page cannot appear for them. A failed navigation is visible to the extension for both HTTP and HTTPS. Alternative: a plain-HTTP block page, rejected for that reason.

**The app serves the block page and shortlist from a local HTTP server.** This keeps the shortlist defined once. The extension redirects to that server. Alternative: copying the shortlist into the extension, rejected because it creates two copies.

**The extension reads the block list and shortlist from the local server.** The server exposes the data the extension needs. Alternative: native messaging, rejected as more setup than the MVP warrants.

**The app runs elevated from startup.** Avoids a UAC prompt in the middle of a session. Alternative: relaunch on demand with a UAC prompt, to be compared in a spike.

**Config is YAML, edited only through the app.** Matches the README. Alternative: a database, rejected as unnecessary for a single small list.

**A `www.` variant is added automatically for each entry.** Closes the easiest bypass. Other subdomains are not covered in the MVP.

**Undo appends a line rather than removing the override.** The override stays in the history, and an undo line is added after it. Undo re-blocks at once. Alternative: deleting the override, rejected because it would hide that the exception was taken.

**Logic lives in a controller, not in the window.** The window only wires widgets to the controller, so the behaviour is tested without creating a Tk window per test. The window is created once, in a smoke test.

## Risks / Trade-offs

- **Brave's new-tab override may not behave as expected.** Mitigation: verify with a short spike before building the extension.
- **Failed-navigation events may not fire for every blocked case.** Mitigation: test with the three example domains, including preloaded ones, and document any gap.
- **The block page is unavailable when the app is closed.** Mitigation: accepted in the proposal; blocks remain in the hosts file, and the redirect falls back to the browser's error page.
- **Running elevated increases the impact of a bug.** Mitigation: the app writes only Blocky-marked lines to the hosts file and never touches other lines.
- **Blocking is not tamper-proof.** Accepted in the README; the user can edit the hosts file directly.

## Spike Results

- **Elevated write, no UAC during a session (spike 1.1):** Blocky started with one UAC prompt. When the schedule opened, it wrote `reddit.com` and `www.reddit.com` to the hosts file, and Windows showed no further prompt. Observed on the owner's machine.
- **Failed navigation in Brave (spike 1.2, partial):** with the extension loaded and the window active, `reddit.com` and `x.com` redirected to Blocky's block page. `youtube.com` was blocked but showed Brave's "no internet connection" page instead of Blocky's. An ordinary failing site showed Brave's normal error page. The cause of the `youtube.com` difference was not investigated; the owner accepts this limitation.
- **New tab in Brave (spike 1.3):** with Blocky running, a new tab showed Blocky's shortlist page. With Blocky closed, a new tab showed the "not running" message.
