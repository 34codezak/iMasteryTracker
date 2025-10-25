import { assertEquals, assertMatch } from "https://deno.land/std@0.225.0/assert/mod.ts";
import { today, offsetDate } from "../scripts/state.js";

Deno.test("today returns an ISO date string", () => {
  const result = today();
  assertMatch(result, /^\d{4}-\d{2}-\d{2}$/);
});

Deno.test("offsetDate applies the provided delta in days", () => {
  const delta = 3;
  const expected = new Date();
  expected.setDate(expected.getDate() + delta);
  const expectedIso = expected.toISOString().slice(0, 10);

  assertEquals(offsetDate(delta), expectedIso);
});

Deno.test("loadState falls back when persistent storage is unavailable", async () => {
  const originalDescriptor = Object.getOwnPropertyDescriptor(globalThis, "localStorage");

  try {
    Object.defineProperty(globalThis, "localStorage", {
      configurable: true,
      writable: true,
      value: undefined
    });

    const module = await import(`../scripts/state.js?scenario=${crypto.randomUUID?.() ?? Math.random()}`);
    const { defaultState, getState, reset } = module;

    try {
      assertEquals(getState(), defaultState);
    } finally {
      reset();
    }
  } finally {
    if (originalDescriptor) {
      Object.defineProperty(globalThis, "localStorage", originalDescriptor);
    } else {
      delete globalThis.localStorage;
    }
  }
});

Deno.test("loadState ignores storages without the required API surface", async () => {
  const originalDescriptor = Object.getOwnPropertyDescriptor(globalThis, "localStorage");

  try {
    const incompleteStorage = {
      getItem: () => null
    };

    Object.defineProperty(globalThis, "localStorage", {
      configurable: true,
      writable: true,
      value: incompleteStorage
    });

    const module = await import(`../scripts/state.js?scenario=${crypto.randomUUID?.() ?? Math.random()}`);
    const { defaultState, getState, reset } = module;

    try {
      assertEquals(getState(), defaultState);
    } finally {
      reset();
    }
  } finally {
    if (originalDescriptor) {
      Object.defineProperty(globalThis, "localStorage", originalDescriptor);
    } else {
      delete globalThis.localStorage;
    }
  }
});
