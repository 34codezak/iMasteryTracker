const DEFAULT_MAX_STORED = 20;
const DEFAULT_DEDUPE_WINDOW = 1000; // ms

function createErrorMonitor(options = {}) {
  const {
    notify,
    target = typeof globalThis !== "undefined" ? globalThis : undefined,
    maxStored = DEFAULT_MAX_STORED,
    dedupeWindow = DEFAULT_DEDUPE_WINDOW,
    now = () => Date.now()
  } = options;

  const entries = [];

  if (!target || typeof target.addEventListener !== "function") {
    return {
      getRecentErrors: () => entries.slice(),
      dispose: () => {},
      record: createRecord(entries, maxStored, notify, () => true)
    };
  }

  let lastKey = null;
  let lastTimestamp = 0;

  const shouldNotify = entry => {
    const key = `${entry.message}|${entry.stack ?? ""}`;
    const timestamp = now();
    if (key === lastKey && timestamp - lastTimestamp < dedupeWindow) {
      lastTimestamp = timestamp;
      return false;
    }
    lastKey = key;
    lastTimestamp = timestamp;
    return true;
  };

  const record = createRecord(entries, maxStored, notify, shouldNotify);

  const handleError = event => {
    const detail = normaliseError(event?.error ?? event);
    detail.type = "error";
    record(detail);
  };

  const handleRejection = event => {
    const detail = normaliseError(event?.reason ?? event);
    detail.type = "unhandledrejection";
    record(detail);
  };

  target.addEventListener("error", handleError);
  target.addEventListener("unhandledrejection", handleRejection);

  return {
    getRecentErrors: () => entries.slice(),
    dispose: () => {
      target.removeEventListener("error", handleError);
      target.removeEventListener("unhandledrejection", handleRejection);
    },
    record
  };
}

function createRecord(entries, maxStored, notify, shouldNotify) {
  return entry => {
    const stamped = {
      ...entry,
      timestamp: entry.timestamp ?? new Date().toISOString()
    };
    entries.push(stamped);
    if (entries.length > maxStored) {
      entries.splice(0, entries.length - maxStored);
    }

    if (shouldNotify(stamped)) {
      const prefix = stamped.type === "unhandledrejection" ? "Unhandled promise rejection" : "Application error";
      const message = formatMessage(prefix, stamped.message);
      if (typeof notify === "function") {
        notify(message);
      }
    }

    if (typeof console !== "undefined" && typeof console.error === "function") {
      console.error(`[iMasteryTracker] ${stamped.type ?? "error"}:`, stamped.message, stamped.stack);
    }

    return stamped;
  };
}

function normaliseError(errorLike) {
  if (errorLike instanceof Error) {
    return {
      message: errorLike.message || "Unknown error",
      stack: errorLike.stack || null
    };
  }

  if (typeof errorLike === "string") {
    return {
      message: errorLike,
      stack: null
    };
  }

  if (errorLike && typeof errorLike === "object") {
    if (typeof errorLike.message === "string") {
      return {
        message: errorLike.message,
        stack: typeof errorLike.stack === "string" ? errorLike.stack : null
      };
    }
    try {
      const serialised = JSON.stringify(errorLike);
      return {
        message: serialised,
        stack: null
      };
    } catch (_) {
      return {
        message: "Unknown error",
        stack: null
      };
    }
  }

  return {
    message: "Unknown error",
    stack: null
  };
}

function formatMessage(prefix, message) {
  const trimmed = String(message ?? "Unknown error").trim();
  if (!trimmed) {
    return prefix;
  }
  return `${prefix}: ${trimmed}`;
}

export { createErrorMonitor, normaliseError };
