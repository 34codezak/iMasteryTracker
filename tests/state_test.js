import { assertEquals, assertMatch } from "https://deno.land/std@0.225.0/testing/asserts.ts";
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
