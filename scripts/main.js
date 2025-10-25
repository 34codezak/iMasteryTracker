import { state, saveState } from "./state.js";
import { renderSprints, openSprintModal, closeSprintModal } from "./ui.js";

const themeToggle = document.getElementById("themeToggle");
const newSprintBtn = document.getElementById("newSprintBtn");
const exportBtn = document.getElementById("exportBtn");
const importFile = document.getElementById("importFile");
const cancelModal = document.getElementById("cancelModal");
const sprintForm = document.getElementById("sprintForm");
const editingId = document.getElementById("editingSprintId");

if (state.ui?.theme === "dark") {
  document.documentElement.classList.add("dark");
}

renderSprints();

themeToggle.onclick = () => {
  document.documentElement.classList.toggle("dark");
  state.ui.theme = document.documentElement.classList.contains("dark") ? "dark" : "light";
  saveState();
};

newSprintBtn.onclick = () => openSprintModal();
cancelModal.onclick = e => { e.preventDefault(); closeSprintModal(); };

sprintForm.onsubmit = e => {
  e.preventDefault();
  const sprintName = document.getElementById("sprintName");
  const sprintNotes = document.getElementById("sprintNotes");
  const sprintStart = document.getElementById("sprintStart");
  const id = editingId.value || crypto.randomUUID();
  const startDate = new Date(sprintStart.value);
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(startDate); d.setDate(d.getDate() + i);
    return { title: `Day ${i+1}`, date: d.toISOString(), done: false, summary: "" };
  });
  const sprint = { id, name: sprintName.value.trim(), start: startDate.toISOString(), notes: sprintNotes.value.trim(), days };
  const idx = state.sprints.findIndex(s => s.id === id);
  if (idx >= 0) state.sprints[idx] = sprint; else state.sprints.unshift(sprint);
  saveState(); renderSprints(); closeSprintModal();
};

exportBtn.onclick = () => {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "imastery-export.json"; a.click();
  URL.revokeObjectURL(url);
};

importFile.onchange = async e => {
  const file = e.target.files[0]; if (!file) return;
  const text = await file.text();
  Object.assign(state, JSON.parse(text));
  saveState(); renderSprints();
};
