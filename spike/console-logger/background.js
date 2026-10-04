// Spike only (HW4 console rerun): the same line Blocky's extension logged during the HW4 spike, and nothing else.
// Nothing is redirected, so with Blocky's own extension turned off each site shows what the hosts file makes of it.
chrome.webNavigation.onErrorOccurred.addListener((details) => {
  console.log("onErrorOccurred", details.url, details.frameId, details.error);
});
