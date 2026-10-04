// Where the extension reads the state; the block page address comes from the state (pageOrigin).
export const APP_ORIGIN = "http://127.0.0.1:8765";

export function shouldRedirect(state, hostname) {
  return Boolean(
    state &&
      state.windowEnd &&
      state.blocked.some((domain) => hostname === domain || hostname.endsWith(`.${domain}`))
  );
}

export function blockPageUrl(state, hostname) {
  const domain = encodeURIComponent(hostname);
  // An app from before blocky.localhost sends no pageOrigin and only knows the old address.
  return state.pageOrigin ? `${state.pageOrigin}/${domain}` : `${APP_ORIGIN}/blocked?domain=${domain}`;
}

export function blockedHostname(state, url) {
  if (!url || !url.startsWith("http")) {
    return null;
  }
  const hostname = new URL(url).hostname;
  return shouldRedirect(state, hostname) ? hostname : null;
}
