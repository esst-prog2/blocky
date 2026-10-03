import { test } from "node:test";
import assert from "node:assert/strict";
import { APP_ORIGIN, blockedHostname, blockPageUrl, shouldRedirect } from "./logic.js";

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

test("redirects a subdomain of a blocked domain", () => {
  assert.equal(shouldRedirect(active, "old.reddit.com"), true);
});

test("redirects a deeper subdomain of a blocked domain", () => {
  assert.equal(shouldRedirect(active, "a.b.reddit.com"), true);
});

test("does not redirect a lookalike domain", () => {
  const xBlocked = { blocked: ["x.com", "www.x.com"], windowEnd: "17:00", shortlist: [] };
  assert.equal(shouldRedirect(xBlocked, "netflix.com"), false);
});

test("does not redirect a subdomain of an overridden domain", () => {
  const overridden = { blocked: ["youtube.com", "www.youtube.com"], windowEnd: "17:00", shortlist: [] };
  assert.equal(shouldRedirect(overridden, "old.reddit.com"), false);
});

test("does not redirect a subdomain when the window is inactive", () => {
  assert.equal(shouldRedirect(inactive, "old.reddit.com"), false);
});

test("block page URL points at the app and encodes the domain", () => {
  assert.equal(blockPageUrl("reddit.com"), `${APP_ORIGIN}/blocked?domain=reddit.com`);
});

test("blockedHostname returns the hostname of a blocked web address", () => {
  assert.equal(blockedHostname(active, "https://old.reddit.com/r/all"), "old.reddit.com");
});

test("blockedHostname ignores addresses that are not web pages", () => {
  assert.equal(blockedHostname(active, "brave://settings"), null);
  assert.equal(blockedHostname(active, undefined), null);
});

test("blockedHostname ignores ordinary and unblocked addresses", () => {
  assert.equal(blockedHostname(active, "https://wikipedia.org/"), null);
  assert.equal(blockedHostname(inactive, "https://reddit.com/"), null);
  assert.equal(blockedHostname(null, "https://reddit.com/"), null);
});
