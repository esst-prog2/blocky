## 1. Code

- [ ] 1.1 Change `shouldRedirect` in `extension/logic.js` so a hostname matches a blocked domain or ends with a dot followed by a blocked domain, and verify with `node --test extension/logic.test.js`
- [ ] 1.2 Add tests to `extension/logic.test.js` for: a subdomain (`old.reddit.com`), a deeper subdomain (`a.b.reddit.com`), a lookalike (`netflix.com` with `x.com` blocked), a subdomain of an overridden domain (not in the blocked list), and an inactive window; verify they all pass
- [ ] 1.3 Run the Python suite (`python -m pytest -q`) and verify it still passes, including the extension file checks

## 2. Docs

- [ ] 2.1 Add to the README risks section that subdomains of blocked sites are blocked only in Brave with the extension, and verify the wording against the spike results

## 3. Brave verification

- [ ] 3.1 Reload the extension, start Blocky in an active window, and verify `old.reddit.com` and `music.youtube.com` show the block page in a new tab
- [ ] 3.2 Verify an open `music.youtube.com` tab is redirected within about a minute of a window starting
- [ ] 3.3 Verify `wikipedia.org` still loads during the window

## 4. Record

- [ ] 4.1 Log the Brave results in `PLANNING_LOG.md`
- [ ] 4.2 Archive this change once the verification passes
