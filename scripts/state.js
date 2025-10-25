const STORAGE_KEY = "imastery-tracker/v2";

const defaultState = {
  theme: "dark",
  createdAt: new Date().toISOString(),
  streams: [
    {
      id: "stream-ignite",
      name: "Deep JavaScript Systems",
      focus: "Patterns, architecture and performance in modern JavaScript.",
      targetDate: offsetDate(21),
      note: "Dial in typed contracts next session.",
      milestones: [
        { id: "mil-1", title: "Map the render lifecycle in depth", complete: true },
        { id: "mil-2", title: "Refine module boundaries for the dashboard", complete: true },
        { id: "mil-3", title: "Ship performance benchmarks", complete: false },
        { id: "mil-4", title: "Document the architecture decisions", complete: false }
      ]
    },
    {
      id: "stream-story",
      name: "Interface Experience Lab",
      focus: "Craft expressive UI systems that scale from mobile to desktop.",
      targetDate: offsetDate(35),
      note: "Collect inspiration to evolve the motion language.",
      milestones: [
        { id: "mil-5", title: "Audit component tokens", complete: true },
        { id: "mil-6", title: "Prototype gesture driven menu", complete: false },
        { id: "mil-7", title: "Usability test round two", complete: false }
      ]
    }
  ],
  habits: [
    {
      id: "habit-setup",
      title: "Write code with intent",
      description: "Plan the day's technical spike before opening the editor.",
      cadence: "Daily",
      streak: 4,
      lastCompleted: offsetDate(-1),
      completeToday: false
    },
    {
      id: "habit-ship",
      title: "Share a learning memo",
      description: "Summarise a key insight in less than five sentences.",
      cadence: "Weekdays",
      streak: 2,
      lastCompleted: offsetDate(-2),
      completeToday: false
    }
  ],
  journal: [
    {
      id: "journal-1",
      date: today(),
      headline: "Friction as a compass",
      focus: "Tracking why certain flows feel heavy led to a better information architecture.",
      takeaways: "Clarity emerges faster when I sketch in words first, pixels second."
    },
    {
      id: "journal-2",
      date: offsetDate(-2),
      headline: "Texture in motion",
      focus: "Curated three references where micro-interactions tell a story.",
      takeaways: "Set aside a dedicated animation review cadence twice a week."
    }
  ]
};

let state = loadState();

function loadState() {
  const storage = getStorage();
  if (!storage) {
    return clone(defaultState);
  }

  try {
    const raw = storage.getItem(STORAGE_KEY);
    if (!raw) {
      return clone(defaultState);
    }
    const parsed = JSON.parse(raw);
    return mergeWithDefaults(parsed, defaultState);
  } catch (error) {
    console.warn("Unable to load saved data, falling back to defaults.", error);
    return clone(defaultState);
  }
}

function mergeWithDefaults(data, fallback) {
  const merged = clone(fallback);
  try {
    return Object.assign(merged, data, {
      streams: Array.isArray(data?.streams) ? data.streams : fallback.streams,
      habits: Array.isArray(data?.habits) ? data.habits : fallback.habits,
      journal: Array.isArray(data?.journal) ? data.journal : fallback.journal
    });
  } catch (_) {
    return merged;
  }
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function persist() {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn("Unable to persist data", error);
  }
}

function mutate(producer) {
  const draft = clone(state);
  producer(draft);
  const changed = JSON.stringify(draft) !== JSON.stringify(state);
  if (changed) {
    state = draft;
    persist();
  }
  return changed;
}

function replace(newState) {
  state = mergeWithDefaults(newState, defaultState);
  persist();
  return state;
}

function reset() {
  state = clone(defaultState);
  persist();
  return state;
}

function createId(prefix) {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return `${prefix}-${crypto.randomUUID()}`;
  }
  return `${prefix}-${Math.random().toString(36).slice(2, 11)}`;
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function offsetDate(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function getStorage() {
  try {
    const storage = globalThis?.localStorage;
    if (typeof storage !== "object" || storage === null) {
      return undefined;
    }

    const hasRequiredMethods =
      typeof storage.getItem === "function" &&
      typeof storage.setItem === "function" &&
      typeof storage.removeItem === "function";
    if (!hasRequiredMethods) {
      return undefined;
    }

    const probeKey = "__imastery-storage-probe__";
    storage.setItem(probeKey, probeKey);
    storage.removeItem(probeKey);

    return storage;
  } catch (_) {
    return undefined;
  }
}

export {
  defaultState,
  getState,
  mutate,
  replace,
  reset,
  persist,
  createId,
  today,
  offsetDate
};

function getState() {
  return state;
}
