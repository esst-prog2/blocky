import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { blockPageUrl } from "./logic.js";

const active = { blocked: ["reddit.com", "www.reddit.com"], windowEnd: "17:00", shortlist: [] };
const listeners = {};
const listen = (name) => ({ addListener: (listener) => (listeners[name] = listener) });
let updates;
let openTabs;
let appAnswer;

globalThis.chrome = {
  webNavigation: { onBeforeNavigate: listen("navigate"), onHistoryStateUpdated: listen("history") },
  alarms: { create: (name, options) => (listeners.alarmCreated = { name, options }), onAlarm: listen("alarm") },
  tabs: {
    update: (tabId, change) => updates.push([tabId, change.url]),
    query: async () => openTabs,
  },
};
globalThis.fetch = async () => appAnswer();
await import("./background.js");

const settle = () => new Promise((resolve) => setTimeout(resolve, 0));
const answers = (state) => () => ({ ok: true, json: async () => state });

beforeEach(() => {
  updates = [];
  openTabs = [];
  appAnswer = answers(active);
});

test("navigating to a blocked site in a tab shows the block page", async () => {
  listeners.navigate({ frameId: 0, tabId: 7, url: "https://old.reddit.com/r/all" });
  await settle();
  assert.deepEqual(updates, [[7, blockPageUrl("old.reddit.com")]]);
});

test("navigating to an unblocked site leaves the tab alone", async () => {
  listeners.navigate({ frameId: 0, tabId: 7, url: "https://wikipedia.org/" });
  await settle();
  assert.deepEqual(updates, []);
});

test("blocked content inside a frame does not redirect the whole tab", async () => {
  listeners.navigate({ frameId: 3, tabId: 7, url: "https://reddit.com/embed" });
  await settle();
  assert.deepEqual(updates, []);
});

test("browser pages are never redirected", async () => {
  listeners.navigate({ frameId: 0, tabId: 7, url: "brave://settings" });
  await settle();
  assert.deepEqual(updates, []);
});

test("in-page navigation to a blocked site shows the block page", async () => {
  listeners.history({ frameId: 0, tabId: 8, url: "https://www.reddit.com/r/all" });
  await settle();
  assert.deepEqual(updates, [[8, blockPageUrl("www.reddit.com")]]);
});

test("nothing is blocked when Blocky is not running", async () => {
  appAnswer = () => {
    throw new TypeError("fetch failed");
  };
  listeners.navigate({ frameId: 0, tabId: 7, url: "https://reddit.com/" });
  await settle();
  assert.deepEqual(updates, []);
});

test("nothing is blocked when Blocky answers with an error", async () => {
  appAnswer = () => ({ ok: false });
  listeners.navigate({ frameId: 0, tabId: 7, url: "https://reddit.com/" });
  await settle();
  assert.deepEqual(updates, []);
});

test("the sweep runs every minute", () => {
  assert.deepEqual(listeners.alarmCreated, { name: "sweep-open-tabs", options: { periodInMinutes: 1 } });
});

test("the sweep sends already open blocked tabs to the block page", async () => {
  openTabs = [
    { id: 1, url: "https://reddit.com/" },
    { id: 2, url: "https://wikipedia.org/" },
    { id: 3, url: "brave://newtab" },
  ];
  await listeners.alarm({ name: "sweep-open-tabs" });
  assert.deepEqual(updates, [[1, blockPageUrl("reddit.com")]]);
});

test("other alarms do not sweep tabs", async () => {
  openTabs = [{ id: 1, url: "https://reddit.com/" }];
  await listeners.alarm({ name: "something-else" });
  assert.deepEqual(updates, []);
});
