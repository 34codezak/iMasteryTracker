import {
  assert,
  assertEquals,
  assertNotStrictEquals,
} from "https://deno.land/std@0.208.0/assert/mod.ts";

const STORAGE_KEY = "imastery-tracker/v2";

function createMockStorage() {
  const store = new Map();
  return {
    store,
    setItemCalls: 0,
    getItem(key) {
      return store.has(key) ? store.get(key) : null;
    },
    setItem(key, value) {
      this.setItemCalls += 1;
      store.set(key, String(value));
    },
    removeItem(key) {
      store.delete(key);
    },
    clear() {
      store.clear();
    },
  };
}

async function loadStateModule() {
  const storage = createMockStorage();
  globalThis.localStorage = storage;
  const mod = await import(`./state.js?cache=${Math.random()}`);
  return { mod, storage };
}

function cleanup() {
  delete globalThis.localStorage;
}

Deno.test("state persistence helpers", async (t) => {
  await t.step("reset returns a fresh clone of defaults", async () => {
    const { mod, storage } = await loadStateModule();
    try {
      const { reset, defaultState } = mod;
      const baseCalls = storage.setItemCalls;
      const first = reset();
      assertEquals(storage.setItemCalls, baseCalls + 1);
      assertEquals(first.streams[0].name, defaultState.streams[0].name);

      // Mutate the returned state and ensure defaults stay intact.
      first.streams[0].name = "Altered";
      const second = reset();
      assertEquals(storage.setItemCalls, baseCalls + 2);
      assertEquals(second.streams[0].name, defaultState.streams[0].name);
      assertNotStrictEquals(second, defaultState);
      assertNotStrictEquals(second, first);
    } finally {
      cleanup();
    }
  });

  await t.step("mutate persists only when state changes", async () => {
    const { mod, storage } = await loadStateModule();
    try {
      const { mutate, getState } = mod;
      const baseCalls = storage.setItemCalls;
      const changed = mutate((draft) => {
        draft.theme = "light";
      });
      assert(changed);
      assertEquals(storage.setItemCalls, baseCalls + 1);
      assertEquals(getState().theme, "light");
      assertEquals(
        storage.store.get(STORAGE_KEY),
        JSON.stringify(getState()),
      );

      const unchanged = mutate(() => {
        // Intentionally no changes.
      });
      assertEquals(unchanged, false);
      assertEquals(storage.setItemCalls, baseCalls + 1);
    } finally {
      cleanup();
    }
  });
});
