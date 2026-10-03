export const APP_ORIGIN = "http://127.0.0.1:8765";

export function shouldRedirect(state, hostname) {
  return Boolean(
    state &&
      state.windowEnd &&
      state.blocked.some((domain) => hostname === domain || hostname.endsWith(`.${domain}`))
  );
}

export function blockPageUrl(hostname) {
  return `${APP_ORIGIN}/blocked?domain=${encodeURIComponent(hostname)}`;
}

export function blockedHostname(state, url) {
  if (!url || !url.startsWith("http")) {
    return null;
  }
  const hostname = new URL(url).hostname;
  return shouldRedirect(state, hostname) ? hostname : null;
}
