import { APP_ORIGIN, blockedHostname, blockPageUrl } from "./logic.js";

async function fetchState() {
  try {
    const response = await fetch(`${APP_ORIGIN}/api/state`);
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  }
}

async function redirectIfBlocked(tabId, url) {
  if (!url.startsWith("http")) {
    return;
  }
  const state = await fetchState();
  const hostname = blockedHostname(state, url);
  if (hostname) {
    chrome.tabs.update(tabId, { url: blockPageUrl(state, hostname) });
  }
}

chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  if (details.frameId === 0) {
    redirectIfBlocked(details.tabId, details.url);
  }
});

chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
  if (details.frameId === 0) {
    redirectIfBlocked(details.tabId, details.url);
  }
});

chrome.alarms.create("sweep-open-tabs", { periodInMinutes: 1 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "sweep-open-tabs") {
    return;
  }
  const state = await fetchState();
  const tabs = await chrome.tabs.query({});
  for (const tab of tabs) {
    const hostname = blockedHostname(state, tab.url);
    if (hostname) {
      chrome.tabs.update(tab.id, { url: blockPageUrl(state, hostname) });
    }
  }
});
