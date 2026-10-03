import { test } from "node:test";
import assert from "node:assert/strict";
import { APP_ORIGIN, blockPageUrl, shouldRedirect } from "./logic.js";

const active = { blocked: ["reddit.com", "www.reddit.com"], windowEnd: "17:00", shortlist: [] };
const inactive = { blocked: [], windowEnd: null, shortlist: [] };

test("redirects a blocked hostname while the window is active", () => {
  assert.equal(shouldRedirect(active, "www.reddit.com"), true);
});

test("does not redirect hostnames that are not blocked", () => {
  assert.equal(shouldRedirect(active, "example.com"), false);
});

test("does not redirect when the window is inactive", () => {
  assert.equal(shouldRedirect(inactive, "reddit.com"), false);
});

test("does not redirect when the app did not answer", () => {
  assert.equal(shouldRedirect(null, "reddit.com"), false);
});

test("block page URL points at the app and encodes the domain", () => {
  assert.equal(blockPageUrl("reddit.com"), `${APP_ORIGIN}/blocked?domain=reddit.com`);
});
