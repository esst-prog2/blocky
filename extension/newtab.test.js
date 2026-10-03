import { test } from "node:test";
import assert from "node:assert/strict";
import { APP_ORIGIN } from "./logic.js";

let run = 0;

async function openNewTab(answer) {
  const message = { hidden: true };
  const opened = [];
  globalThis.document = { getElementById: (id) => (id === "message" ? message : null) };
  globalThis.location = { replace: (url) => opened.push(url) };
  globalThis.fetch = async () => answer();
  run += 1;
  await import(`./newtab.js?run=${run}`);
  await new Promise((resolve) => setTimeout(resolve, 0));
  return { message, opened };
}

test("a new tab opens Blocky's page when the app is running", async () => {
  const { message, opened } = await openNewTab(() => ({ ok: true }));
  assert.deepEqual(opened, [`${APP_ORIGIN}/`]);
  assert.equal(message.hidden, true);
});

test("a new tab explains Blocky is not running when the app does not answer", async () => {
  const { message, opened } = await openNewTab(() => {
    throw new TypeError("fetch failed");
  });
  assert.deepEqual(opened, []);
  assert.equal(message.hidden, false);
});

test("a new tab shows the message when the app answers with an error", async () => {
  const { message, opened } = await openNewTab(() => ({ ok: false, status: 500 }));
  assert.deepEqual(opened, []);
  assert.equal(message.hidden, false);
});
