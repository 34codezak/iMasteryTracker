import {
  getState,
  mutate,
  replace,
  reset,
  createId,
  today
} from "./state.js";

const selectors = {
  streamList: "streamList",
  habitList: "habitList",
  journalList: "journalList",
  importInput: "importInput"
};

const dialogs = {
  stream: document.getElementById("streamDialog"),
  journal: document.getElementById("journalDialog")
};

const forms = {
  stream: document.getElementById("streamForm"),
  journal: document.getElementById("journalForm")
};

const buttons = {
  theme: document.getElementById("themeToggle"),
  export: document.getElementById("exportBtn"),
  reset: document.getElementById("resetBtn"),
  newStream: document.getElementById("newStreamBtn"),
  newEntry: document.getElementById("newJournalBtn")
};

const overviewEls = {
  streams: document.querySelector("[data-stat='streams'] strong"),
  monthlyValue: document.querySelector("[data-stat='completion'] [data-progress-value]"),
  monthlyDial: document.querySelector("[data-stat='completion'] .metric-progress-dial"),
  monthlySubtext: document.querySelector("[data-stat='completion'] [data-progress-subtext]"),
  milestones: document.querySelector("[data-stat='milestones'] strong"),
  habits: document.querySelector("[data-stat='habits'] strong")
};

const layout = {
  heroActions: document.getElementById("heroActions"),
  menuToggle: document.getElementById("menuToggle"),
  sidebarBackdrop: document.getElementById("sidebarBackdrop"),
  mobileMedia: typeof window !== "undefined" && window.matchMedia ? window.matchMedia("(max-width: 720px)") : null
};

const heroSubtext = document.getElementById("heroSubtext");

init();

function init() {
  syncHabitCompletion();
  applyTheme(getState().theme ?? "dark");
  renderAll();
  bindEvents();
  toggleSidebar(false);
}

function bindEvents() {
  buttons.theme?.addEventListener("click", () => {
    const nextTheme = document.documentElement.classList.toggle("theme-light") ? "light" : "dark";
    mutate(state => {
      state.theme = nextTheme === "light" ? "light" : "dark";
    });
  });

  buttons.export?.addEventListener("click", handleExport);
  document.getElementById(selectors.importInput)?.addEventListener("change", handleImport);
  buttons.reset?.addEventListener("click", handleReset);
  buttons.newStream?.addEventListener("click", startCreateStream);
  buttons.newEntry?.addEventListener("click", () => openDialog(dialogs.journal));

  dialogs.stream?.querySelector("[data-dismiss]")?.addEventListener("click", () => {
    closeDialog(dialogs.stream);
    resetStreamFormState();
  });
  dialogs.journal?.querySelector("[data-dismiss]")?.addEventListener("click", () => closeDialog(dialogs.journal));

  dialogs.stream?.addEventListener("close", resetStreamFormState);

  forms.stream?.addEventListener("submit", handleStreamSubmit);
  forms.journal?.addEventListener("submit", handleJournalSubmit);

  const streamContainer = document.getElementById(selectors.streamList);
  streamContainer?.addEventListener("change", handleStreamCheckbox);
  streamContainer?.addEventListener("input", handleStreamNoteInput);
  streamContainer?.addEventListener("click", handleStreamActions);

  const habitContainer = document.getElementById(selectors.habitList);
  habitContainer?.addEventListener("change", handleHabitToggle);

  layout.menuToggle?.addEventListener("click", () => toggleSidebar());
  layout.sidebarBackdrop?.addEventListener("click", () => toggleSidebar(false));

  const handleMediaChange = event => {
    if (!event.matches) {
      toggleSidebar(false);
    } else {
      toggleSidebar(false);
    }
  };

  if (layout.mobileMedia) {
    if (typeof layout.mobileMedia.addEventListener === "function") {
      layout.mobileMedia.addEventListener("change", handleMediaChange);
    } else if (typeof layout.mobileMedia.addListener === "function") {
      layout.mobileMedia.addListener(handleMediaChange);
    }
  }

  document.addEventListener("keydown", handleGlobalKeydown);
}

function renderAll() {
  const state = getState();
  renderOverview(state);
  renderStreams(state.streams);
  renderHabits(state.habits);
  renderJournal(state.journal);
}

function renderOverview(state) {
  const streams = state.streams ?? [];
  const habits = state.habits ?? [];
  const journalEntries = state.journal ?? [];
  const totalMilestones = streams.reduce((sum, s) => sum + (s.milestones?.length ?? 0), 0);
  const completedMilestones = streams.reduce(
    (sum, s) => sum + (s.milestones?.filter(m => m.complete).length ?? 0),
    0
  );
  const completionPct = totalMilestones ? Math.round((completedMilestones / totalMilestones) * 100) : 0;
  const activeHabits = habits.filter(h => h.completeToday).length;
  const journalCount = journalEntries.length;
  const now = new Date();
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const monthPct = clampPercent(daysInMonth ? (now.getDate() / daysInMonth) * 100 : 0);

  if (overviewEls.streams) overviewEls.streams.textContent = String(streams.length).padStart(2, "0");
  if (overviewEls.monthlyValue) overviewEls.monthlyValue.textContent = `${monthPct}%`;
  if (overviewEls.monthlyDial) {
    overviewEls.monthlyDial.style.setProperty("--progress", (monthPct / 100).toFixed(4));
    overviewEls.monthlyDial.setAttribute("aria-valuenow", String(monthPct));
    overviewEls.monthlyDial.setAttribute("aria-valuetext", `${monthPct}% of the month complete`);
  }
  if (overviewEls.monthlySubtext) {
    overviewEls.monthlySubtext.textContent = `Milestone momentum ${completionPct}%`;
  }
  if (overviewEls.milestones) overviewEls.milestones.textContent = `${completedMilestones}/${totalMilestones || 0}`;
  if (overviewEls.habits) overviewEls.habits.textContent = activeHabits.toString().padStart(2, "0");

  if (heroSubtext) {
    heroSubtext.textContent = `Currently guiding ${streams.length} learning stream${streams.length === 1 ? "" : "s"} with ${totalMilestones} milestone${totalMilestones === 1 ? "" : "s"} in motion while ${monthPct}% of the month has unfolded and milestone momentum holds at ${completionPct}%. ${journalCount} reflection${journalCount === 1 ? "" : "s"} captured.`;
  }
}

function renderStreams(streams) {
  const container = document.getElementById(selectors.streamList);
  if (!container) return;
  container.innerHTML = "";

  if (!streams.length) {
    container.appendChild(createEmptyState("Create your first stream to anchor the work."));
    return;
  }

  streams.forEach(stream => {
    container.appendChild(renderStreamCard(stream));
  });
}

function renderStreamCard(stream) {
  const card = document.createElement("article");
  card.className = "stream-card";
  card.dataset.streamId = stream.id;

  const total = stream.milestones?.length ?? 0;
  const completed = stream.milestones?.filter(m => m.complete).length ?? 0;
  const pct = total ? Math.round((completed / total) * 100) : 0;
  const dueCopy = describeDueDate(stream.targetDate);

  card.innerHTML = `
    <div class="stream-top">
      <div class="stream-title">
        <h3>${escapeHtml(stream.name)}</h3>
        <div class="stream-focus">${escapeHtml(stream.focus ?? "")}</div>
      </div>
      <div class="stream-meta">
        <span class="due">${dueCopy}</span>
        <div class="stream-actions">
          <button class="icon-btn" type="button" data-action="edit-stream" aria-label="Edit ${escapeHtml(stream.name)}">
            <i class="fa-solid fa-pen-to-square" aria-hidden="true"></i>
          </button>
          <button class="icon-btn" type="button" data-action="remove-stream" aria-label="Remove ${escapeHtml(stream.name)}">
            <i class="fa-solid fa-trash-can" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    </div>
    <div class="progress">
      <div class="progress-bar"><span style="width:${pct}%"></span></div>
      <div class="progress-info">
        <span>${completed} / ${total} milestones</span>
        <span>${pct}%</span>
      </div>
    </div>
    <div class="milestone-list">
      ${renderMilestones(stream)}
    </div>
    <textarea class="stream-note" placeholder="Capture the next move" data-role="stream-note" data-stream="${stream.id}">${escapeHtml(stream.note ?? "")}</textarea>
  `;

  return card;
}

function startCreateStream() {
  resetStreamFormState();
  openDialog(dialogs.stream);
}

function startEditStream(streamId) {
  const state = getState();
  const stream = state.streams?.find(s => s.id === streamId);
  if (!stream || !forms.stream) return;

  resetStreamFormState();

  forms.stream.dataset.streamId = stream.id;
  forms.stream.dataset.mode = "edit";

  const titleEl = dialogs.stream?.querySelector("#streamDialogTitle");
  if (titleEl) {
    titleEl.textContent = "Edit learning stream";
  }

  const submitBtn = forms.stream.querySelector("button[type='submit']");
  if (submitBtn) {
    submitBtn.textContent = "Save changes";
  }

  const nameField = forms.stream.querySelector("[name='streamName']");
  if (nameField instanceof HTMLInputElement) {
    nameField.value = stream.name ?? "";
  }

  const focusField = forms.stream.querySelector("[name='streamFocus']");
  if (focusField instanceof HTMLInputElement) {
    focusField.value = stream.focus ?? "";
  }

  const dateField = forms.stream.querySelector("[name='streamDate']");
  if (dateField instanceof HTMLInputElement) {
    dateField.value = stream.targetDate ?? today();
  }

  const noteField = forms.stream.querySelector("[name='streamNote']");
  if (noteField instanceof HTMLTextAreaElement) {
    noteField.value = stream.note ?? "";
  }

  const milestonesField = forms.stream.querySelector("[name='streamMilestones']");
  if (milestonesField instanceof HTMLTextAreaElement) {
    milestonesField.value = (stream.milestones ?? []).map(m => m.title ?? "").join("\n");
  }

  openDialog(dialogs.stream);
}

function renderMilestones(stream) {
  if (!stream.milestones?.length) {
    return `<div class="empty-state">Add milestones to chart progress.</div>`;
  }
  return stream.milestones
    .map(milestone => {
      const classes = ["milestone", milestone.complete ? "complete" : ""].filter(Boolean).join(" ");
      return `
        <div class="${classes}" data-milestone-id="${milestone.id}">
          <label>
            <input type="checkbox" data-stream="${stream.id}" data-milestone="${milestone.id}" ${milestone.complete ? "checked" : ""} />
            <span>
              <span class="title">${escapeHtml(milestone.title)}</span>
              <span class="meta">${milestone.complete ? "Locked in" : "In progress"}</span>
            </span>
          </label>
          <button class="icon-btn" type="button" data-action="edit-milestone" data-stream="${stream.id}" data-milestone="${milestone.id}" aria-label="Edit deliverable ${escapeHtml(milestone.title)}">
            <i class="fa-solid fa-pen" aria-hidden="true"></i>
          </button>
        </div>
      `;
    })
    .join("");
}

function renderHabits(habits) {
  const container = document.getElementById(selectors.habitList);
  if (!container) return;
  container.innerHTML = "";

  if (!habits.length) {
    container.appendChild(createEmptyState("Define one ritual that keeps you honest."));
    return;
  }

  habits.forEach(habit => {
    const item = document.createElement("article");
    item.className = "habit";
    item.innerHTML = `
      <div class="habit-top">
        <label>
          <input type="checkbox" data-habit="${habit.id}" ${habit.completeToday ? "checked" : ""} />
          <span>${escapeHtml(habit.title)}</span>
        </label>
        <span class="streak">${habit.streak} day streak</span>
      </div>
      <div class="habit-meta">${escapeHtml(habit.description ?? "")}</div>
      <div class="habit-meta">Cadence: ${escapeHtml(habit.cadence ?? "" )}</div>
    `;
    container.appendChild(item);
  });
}

function renderJournal(entries) {
  const container = document.getElementById(selectors.journalList);
  if (!container) return;
  container.innerHTML = "";

  if (!entries.length) {
    container.appendChild(createEmptyState("Log reflections to turn insight into action."));
    return;
  }

  entries
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : -1))
    .slice(0, 6)
    .forEach(entry => {
      const article = document.createElement("article");
      article.className = "journal-entry";
      article.innerHTML = `
        <h4>${escapeHtml(entry.headline ?? "Untitled insight")}</h4>
        <div class="date">${formatDate(entry.date)}</div>
        <p>${escapeHtml(entry.focus ?? "")}</p>
        ${entry.takeaways ? `<div class="tags"><span class="tag">${escapeHtml(entry.takeaways)}</span></div>` : ""}
      `;
      container.appendChild(article);
    });
}

function handleStreamSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const name = (formData.get("streamName") ?? "").toString().trim();
  if (!name) {
    form.querySelector("[name='streamName']")?.focus();
    return;
  }

  const focus = (formData.get("streamFocus") ?? "").toString().trim();
  const targetDate = (formData.get("streamDate") ?? today()).toString();
  const note = (formData.get("streamNote") ?? "").toString();
  const milestoneLines = (formData.get("streamMilestones") ?? "").toString()
    .split("\n")
    .map(line => line.trim())
    .filter(Boolean);
  const editingId = form.dataset.streamId;

  if (editingId) {
    mutate(state => {
      const stream = state.streams?.find(s => s.id === editingId);
      if (!stream) return;
      stream.name = name;
      stream.focus = focus;
      stream.targetDate = targetDate;
      stream.note = note;
      const existingMilestones = stream.milestones ?? [];
      const nextMilestones = milestoneLines.map((line, index) => {
        const current = existingMilestones[index];
        if (current) {
          return { ...current, title: line };
        }
        return { id: createId("milestone"), title: line, complete: false };
      });
      stream.milestones = nextMilestones;
    });
  } else {
    mutate(state => {
      const stream = {
        id: createId("stream"),
        name,
        focus,
        targetDate,
        note,
        milestones: milestoneLines.map(line => ({ id: createId("milestone"), title: line, complete: false }))
      };
      state.streams = [stream, ...(state.streams ?? [])];
    });
  }

  closeDialog(dialogs.stream);
  renderAll();
}

function handleJournalSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const headline = (formData.get("journalHeadline") ?? "").toString().trim();
  const focus = (formData.get("journalFocus") ?? "").toString().trim();
  const takeaways = (formData.get("journalTakeaways") ?? "").toString().trim();
  const date = (formData.get("journalDate") ?? today()).toString();

  mutate(state => {
    const entry = {
      id: createId("journal"),
      headline,
      focus,
      takeaways,
      date
    };
    state.journal = [entry, ...(state.journal ?? [])];
  });

  closeDialog(dialogs.journal);
  form.reset();
  const dateField = form.querySelector("[name='journalDate']");
  if (dateField) {
    dateField.value = today();
  }
  renderAll();
}

function handleStreamCheckbox(event) {
  const target = event.target;
  if (!(target instanceof HTMLInputElement) || !target.dataset.milestone) return;
  const streamId = target.dataset.stream;
  const milestoneId = target.dataset.milestone;

  mutate(state => {
    const stream = state.streams?.find(s => s.id === streamId);
    const milestone = stream?.milestones?.find(m => m.id === milestoneId);
    if (milestone) {
      milestone.complete = target.checked;
    }
  });
  renderAll();
}

function handleStreamNoteInput(event) {
  const target = event.target;
  if (!(target instanceof HTMLTextAreaElement) || target.dataset.role !== "stream-note") return;
  const streamId = target.dataset.stream;

  mutate(state => {
    const stream = state.streams?.find(s => s.id === streamId);
    if (stream) {
      stream.note = target.value;
    }
  });
}

function handleStreamActions(event) {
  const actionButton = event.target.closest?.("[data-action]");
  if (!actionButton) return;

  const streamCard = actionButton.closest("[data-stream-id]");
  const streamId = streamCard?.dataset.streamId;
  if (!streamId) return;

  const action = actionButton.dataset.action;

  if (action === "remove-stream") {
    mutate(state => {
      state.streams = (state.streams ?? []).filter(stream => stream.id !== streamId);
    });
    renderAll();
    return;
  }

  if (action === "edit-stream") {
    startEditStream(streamId);
    return;
  }

  if (action === "edit-milestone") {
    const milestoneId = actionButton.dataset.milestone;
    if (!milestoneId) return;
    const state = getState();
    const stream = state.streams?.find(s => s.id === streamId);
    const milestone = stream?.milestones?.find(m => m.id === milestoneId);
    if (!milestone) return;
    const nextTitle = prompt("Update deliverable title", milestone.title ?? "");
    if (nextTitle == null) return;
    const trimmed = nextTitle.trim();
    if (!trimmed) return;
    mutate(current => {
      const currentStream = current.streams?.find(s => s.id === streamId);
      const currentMilestone = currentStream?.milestones?.find(m => m.id === milestoneId);
      if (currentMilestone) {
        currentMilestone.title = trimmed;
      }
    });
    renderAll();
    return;
  }
}

function handleHabitToggle(event) {
  const target = event.target;
  if (!(target instanceof HTMLInputElement) || !target.dataset.habit) return;
  const habitId = target.dataset.habit;
  const checked = target.checked;
  const todayStamp = today();
  const yesterday = new Date(todayStamp);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStamp = yesterday.toISOString().slice(0, 10);

  mutate(state => {
    const habit = state.habits?.find(h => h.id === habitId);
    if (!habit) return;

    if (checked) {
      if (habit.lastCompleted === todayStamp) {
        habit.completeToday = true;
        return;
      }
      if (habit.lastCompleted === yesterdayStamp) {
        habit.streak = (habit.streak ?? 0) + 1;
      } else {
        habit.streak = 1;
      }
      habit.lastCompleted = todayStamp;
      habit.completeToday = true;
    } else {
      habit.completeToday = false;
    }
  });
  renderAll();
}

function syncHabitCompletion() {
  const todayStamp = today();
  mutate(state => {
    (state.habits ?? []).forEach(habit => {
      habit.completeToday = habit.lastCompleted === todayStamp;
    });
  });
}

function handleGlobalKeydown(event) {
  if (event.key !== "Escape") return;
  if (layout.heroActions?.classList.contains("is-open")) {
    toggleSidebar(false);
    layout.menuToggle?.focus();
  }
}

function toggleSidebar(force) {
  const actions = layout.heroActions;
  if (!actions) return;

  const isMobile = layout.mobileMedia
    ? layout.mobileMedia.matches
    : typeof window !== "undefined"
      ? window.innerWidth <= 720
      : false;
  const requestedOpen = typeof force === "boolean" ? force : !actions.classList.contains("is-open");
  const shouldOpen = isMobile ? requestedOpen : false;
  const icon = layout.menuToggle?.querySelector?.("i");

  actions.classList.toggle("is-open", shouldOpen);
  const hidden = isMobile ? !shouldOpen : false;
  actions.setAttribute("aria-hidden", hidden ? "true" : "false");

  if (layout.menuToggle) {
    layout.menuToggle.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
    layout.menuToggle.setAttribute("aria-label", shouldOpen ? "Close sidebar menu" : "Open sidebar menu");
  }

  if (icon) {
    icon.classList.toggle("fa-bars", !shouldOpen);
    icon.classList.toggle("fa-xmark", shouldOpen);
  }

  if (layout.sidebarBackdrop) {
    if (shouldOpen) {
      layout.sidebarBackdrop.removeAttribute("hidden");
    } else {
      layout.sidebarBackdrop.setAttribute("hidden", "");
    }
    layout.sidebarBackdrop.classList.toggle("is-active", shouldOpen);
  }

  document.body.classList.toggle("sidebar-open", shouldOpen);
}

function handleExport() {
  const state = getState();
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "imastery-tracker.json";
  anchor.click();
  URL.revokeObjectURL(url);
}

async function handleImport(event) {
  const input = event.target;
  const file = input.files?.[0];
  if (!file) return;

  try {
    const text = await file.text();
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== "object") {
      throw new Error("Invalid file structure");
    }
    replace(parsed);
    renderAll();
  } catch (error) {
    alert("We could not import that file. Please ensure it was exported from iMasteryTracker.");
    console.error(error);
  } finally {
    input.value = "";
  }
}

function handleReset() {
  if (!confirm("Reset everything back to the starter workspace?")) {
    return;
  }
  reset();
  renderAll();
}

function resetStreamFormState() {
  if (!forms.stream) return;
  forms.stream.reset();
  delete forms.stream.dataset.streamId;
  delete forms.stream.dataset.mode;

  const titleEl = dialogs.stream?.querySelector("#streamDialogTitle");
  if (titleEl) {
    titleEl.textContent = "New learning stream";
  }

  const submitBtn = forms.stream.querySelector("button[type='submit']");
  if (submitBtn) {
    submitBtn.textContent = "Create stream";
  }

  const milestonesField = forms.stream.querySelector("[name='streamMilestones']");
  if (milestonesField instanceof HTMLTextAreaElement) {
    milestonesField.value = "";
  }
}

function openDialog(dialog) {
  if (!dialog) return;
  if (dialog.id === "streamDialog") {
    const dateField = dialog.querySelector("[name='streamDate']");
    if (dateField && !dateField.value) {
      dateField.value = today();
    }
  }
  if (dialog.id === "journalDialog") {
    const dateField = dialog.querySelector("[name='journalDate']");
    if (dateField) {
      dateField.value = today();
    }
  }
  dialog.showModal();
}

function closeDialog(dialog) {
  if (!dialog) return;
  dialog.close();
}

function describeDueDate(targetDate) {
  if (!targetDate) return "Open";
  const target = new Date(targetDate);
  const todayDate = new Date(today());
  const diff = Math.round((target - todayDate) / (1000 * 60 * 60 * 24));
  if (Number.isNaN(diff)) return "Open";
  if (diff < -1) return `${Math.abs(diff)} days ago`;
  if (diff === -1) return "Yesterday";
  if (diff === 0) return "Today";
  if (diff === 1) return "Tomorrow";
  return `Due in ${diff} days`;
}

function createEmptyState(message) {
  const el = document.createElement("div");
  el.className = "empty-state";
  el.textContent = message;
  return el;
}

function escapeHtml(value) {
  const text = value == null ? "" : String(value);
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function clampPercent(value) {
  if (!Number.isFinite(value)) return 0;
  if (value <= 0) return 0;
  if (value >= 100) return 100;
  return Math.round(value);
}

function formatDate(date) {
  const value = date ? new Date(date) : new Date();
  if (Number.isNaN(value.getTime())) return "";
  return value.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric"
  });
}

function applyTheme(theme) {
  document.documentElement.classList.toggle("theme-light", theme === "light");
}
