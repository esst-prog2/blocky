## Why

During an active window, subdomains of blocked sites are not blocked. The subdomains spike (spike/subdomains/results.md) found that old.reddit.com and music.youtube.com load normally, and new.reddit.com, m.youtube.com and mobile.x.com reach Blocky's page only because those sites redirect to the main domain. The hosts file holds only exact names, so it cannot cover every subdomain.

## What Changes

- In Brave, the extension treats any subdomain of a blocked domain as blocked: `old.reddit.com` is redirected to the block page when `reddit.com` is blocked. This applies to new navigations, in-page changes and the one-minute check of open tabs.
- Subdomains of a domain with an active override are not redirected, as the domain itself is not.
- The hosts file is unchanged: it still holds each domain and its `www.` variant.
- **BREAKING (spec):** the rule that the extension never decides what is blocked is relaxed. Subdomains are blocked only by the extension, so with the extension disabled, or in browsers and windows without it, they load.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `browser-extension`: the redirect requirement covers subdomains of blocked domains, and the "Extension does not block on its own" requirement allows the extension to block those subdomains.

## Impact

- `extension/logic.js`: the hostname check matches a blocked domain or any subdomain of it.
- `extension/logic.test.js`: tests for subdomain matching, for lookalike domains that must not match, and for overrides.
- `README.md`: the risks section states that subdomains are blocked only in Brave with the extension.
- Must be verified in Brave: old.reddit.com and music.youtube.com show the block page during an active window.
