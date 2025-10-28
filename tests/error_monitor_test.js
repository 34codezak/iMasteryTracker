import { assertEquals, assert } from "https://deno.land/std@0.225.0/assert/mod.ts";
import { createErrorMonitor, normaliseError } from "../scripts/error-monitor.js";

Deno.test("normaliseError handles strings and objects", () => {
  const errInstance = normaliseError(new Error("boom"));
  assertEquals(errInstance.message, "boom");
  assert(errInstance.stack && errInstance.stack.includes("boom"));

  const errString = normaliseError("boom");
  assertEquals(errString.message, "boom");
  assertEquals(errString.stack, null);

  const errObject = normaliseError({ message: "oops", stack: "stack" });
  assertEquals(errObject.message, "oops");
  assertEquals(errObject.stack, "stack");

  const errUnknown = normaliseError({});
  assertEquals(errUnknown.message, "{}");
});

Deno.test("createErrorMonitor records errors and notifies once per window", () => {
  const target = new EventTarget();
  const notifications = [];
  const times = [0, 200, 1500];
  const monitor = createErrorMonitor({
    notify: message => notifications.push(message),
    target,
    now: () => times.shift() ?? 2000,
    dedupeWindow: 1000,
    maxStored: 5
  });

  target.dispatchEvent(new ErrorEvent("error", { error: new Error("Primary failure") }));
  target.dispatchEvent(new ErrorEvent("error", { error: new Error("Primary failure") }));
  target.dispatchEvent(new ErrorEvent("error", { error: new Error("Primary failure") }));

  assertEquals(notifications.length, 2);
  assert(notifications[0].includes("Primary failure"));
  assert(notifications[1].includes("Primary failure"));

  const stored = monitor.getRecentErrors();
  assertEquals(stored.length, 3);
  assert(stored.every(entry => entry.type === "error"));

  monitor.dispose();
});

Deno.test("createErrorMonitor caps stored entries", () => {
  const target = new EventTarget();
  const monitor = createErrorMonitor({
    target,
    notify: () => {},
    dedupeWindow: 0,
    maxStored: 2
  });

  target.dispatchEvent(new ErrorEvent("error", { error: new Error("First") }));
  target.dispatchEvent(new ErrorEvent("error", { error: new Error("Second") }));
  target.dispatchEvent(new ErrorEvent("error", { error: new Error("Third") }));

  const stored = monitor.getRecentErrors();
  assertEquals(stored.length, 2);
  assertEquals(stored[0].message, "Second");
  assertEquals(stored[1].message, "Third");

  monitor.dispose();
});

Deno.test("createErrorMonitor handles promise rejections", () => {
  const target = new EventTarget();
  const notifications = [];
  const monitor = createErrorMonitor({
    notify: message => notifications.push(message),
    target,
    now: () => Date.now(),
    dedupeWindow: 0,
    maxStored: 2
  });

  target.dispatchEvent(
    new PromiseRejectionEvent("unhandledrejection", { reason: new Error("Rejected") })
  );

  assertEquals(notifications.length, 1);
  assert(notifications[0].startsWith("Unhandled promise rejection"));
  const stored = monitor.getRecentErrors();
  assertEquals(stored.length, 1);
  assertEquals(stored[0].type, "unhandledrejection");

  monitor.dispose();
});
