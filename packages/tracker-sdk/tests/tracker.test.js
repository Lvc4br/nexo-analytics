import assert from "node:assert/strict";
import { test } from "node:test";
import { createNexoTracker } from "../src/index.js";

function installBrowser({ doNotTrack = null } = {}) {
  const requests = [];
  const listeners = new Map();
  const stored = new Map();
  const originalPushState = function (_state, _title, url) {
    if (url) window.location.pathname = new URL(url, "https://portfolio.example").pathname;
  };
  const originalReplaceState = function (_state, _title, url) {
    if (url) window.location.pathname = new URL(url, "https://portfolio.example").pathname;
  };
  globalThis.window = {
    __nexoAnalyticsDisabled: false,
    location: { hostname: "portfolio.example", pathname: "/", search: "?private=yes", hash: "#top" },
    navigator: { doNotTrack },
    history: { pushState: originalPushState, replaceState: originalReplaceState },
    addEventListener: (name, callback) => listeners.set(name, callback),
    removeEventListener: (name) => listeners.delete(name),
  };
  globalThis.sessionStorage = {
    getItem: (key) => stored.get(key) ?? null,
    setItem: (key, value) => stored.set(key, value),
  };
  globalThis.fetch = (_endpoint, request) => {
    requests.push(JSON.parse(request.body));
    return Promise.resolve({ ok: true });
  };
  return { requests, listeners, originalPushState, originalReplaceState };
}

test("collects path-only page and custom events and observes SPA navigation", async () => {
  const { requests, originalPushState, originalReplaceState } = installBrowser();
  const tracker = createNexoTracker({ endpoint: "https://nexo.example/api/v1/collect", siteId: "portfolio", trackDevelopment: true });

  assert.equal(requests.length, 1);
  assert.equal(requests[0].event_name, "page_view");
  assert.equal(requests[0].path, "/");
  assert.equal("search" in requests[0], false);
  assert.equal("hash" in requests[0], false);

  window.history.pushState({}, "", "/contact?email=private@example.com");
  await new Promise((resolve) => setImmediate(resolve));
  tracker.track("contact_click");
  tracker.track("bad event name");

  assert.equal(requests.length, 3);
  assert.equal(requests[1].event_name, "page_view");
  assert.equal(requests[1].path, "/contact");
  assert.equal(requests[2].event_name, "contact_click");
  assert.equal(requests[2].path, "/contact");
  assert.equal(requests[0].session_id, requests[2].session_id);

  tracker.destroy();
  assert.equal(window.history.pushState, originalPushState);
  assert.equal(window.history.replaceState, originalReplaceState);
});

test("does not collect when Do Not Track is enabled", () => {
  const { requests } = installBrowser({ doNotTrack: "1" });
  const tracker = createNexoTracker({ endpoint: "https://nexo.example/api/v1/collect", siteId: "portfolio", trackDevelopment: true });
  tracker.track("contact_click");
  assert.equal(requests.length, 0);
  tracker.destroy();
});

test("stays inactive if deployment settings are missing", () => {
  const { requests } = installBrowser();
  const tracker = createNexoTracker();
  tracker.track("contact_click");
  assert.equal(requests.length, 0);
  tracker.destroy();
});
