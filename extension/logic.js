export const APP_ORIGIN = "http://127.0.0.1:8765";

export function shouldRedirect(state, hostname) {
  return Boolean(state && state.windowEnd && state.blocked.includes(hostname));
}

export function blockPageUrl(hostname) {
  return `${APP_ORIGIN}/blocked?domain=${encodeURIComponent(hostname)}`;
}
