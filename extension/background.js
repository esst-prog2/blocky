import { APP_ORIGIN, blockPageUrl, shouldRedirect } from "./logic.js";

async function fetchState() {
  try {
    const response = await fetch(`${APP_ORIGIN}/api/state`);
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  }
}

chrome.webNavigation.onErrorOccurred.addListener(async (details) => {
  console.log("onErrorOccurred", details.url, details.frameId, details.error);
  if (details.frameId !== 0 || !details.url.startsWith("http")) {
    return;
  }
  const hostname = new URL(details.url).hostname;
  const state = await fetchState();
  if (shouldRedirect(state, hostname)) {
    chrome.tabs.update(details.tabId, { url: blockPageUrl(hostname) });
  }
});
