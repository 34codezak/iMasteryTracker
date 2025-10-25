import { state, saveState } from "./state.js";

export function renderSprints() {
  const container = document.getElementById("sprints");
  container.innerHTML = "";
  state.sprints.forEach(s => container.appendChild(renderSprint(s)));
}


function renderSprint(s) {
  const tpl = document.getElementById("sprintTpl").content.cloneNode(true);
  tpl.querySelector(".sprint__name").textContent = s.name;
  const start = new Date(s.start);
  const end = new Date(start); end.setDate(end.getDate() + 6);
  tpl.querySelector(".sprint__meta").textContent = `${fmtDate(start)} → ${fmtDate(end)}`;
  const pct = Math.round((s.days.filter(d => d.done).length / s.days.length) * 100);
  tpl.querySelector(".pct").textContent = pct + "%";
  tpl.querySelector(".fg").style.strokeDashoffset = 339.292 * (1 - pct / 100);

  const editBtn = tpl.querySelector(".edit");
  const delBtn = tpl.querySelector(".delete");
  editBtn.setAttribute("aria-label", `Edit sprint "${s.name}"`);
  delBtn.setAttribute("aria-label", `Delete sprint "${s.name}"`);
  editBtn.onclick = () => openSprintModal(s);
  delBtn.onclick = () => openDeleteModal(s);

  const daysEl = tpl.querySelector(".days");
  s.days.forEach((d, i) => daysEl.appendChild(renderDay(s, i, d)));
  return tpl;
}


/**
 * Renders a single day element to the DOM.
 *
 * @param {Object} s - Sprint object from state
 * @param {Number} i - Index of the day in the sprint
 * @param {Object} d - Day object from state
 * @returns {HTMLElement} - Rendered day element
 */
function renderDay(s, i, d) {
  const tpl = document.getElementById("dayTpl").content.cloneNode(true);
  tpl.querySelector(".day__title").textContent = d.title;
  tpl.querySelector(".day__date").textContent = fmtDate(new Date(d.date));
  const chk = tpl.querySelector(".day__check"), ta = tpl.querySelector(".day__summary");
  chk.checked = d.done; ta.value = d.summary;
  chk.onchange = () => { d.done = chk.checked; saveState(); renderSprints(); };
  ta.oninput = () => { d.summary = ta.value; saveState(); };
  return tpl;
}


/**
 * Opens the sprint modal for creating or editing a sprint.
 * If a sprint is provided, the modal will be pre-filled with the sprint's data.
 * If no sprint is provided, the modal will be empty and the title will be "New Sprint".
 * @param {Object} sprint - Optional sprint object to pre-fill the modal with.
 */
export function openSprintModal(sprint = null) {
  const modal = document.getElementById("sprintModal");
  const sprintName = document.getElementById("sprintName");
  const sprintNotes = document.getElementById("sprintNotes");
  const sprintStart = document.getElementById("sprintStart");
  const editingId = document.getElementById("editingSprintId");

  if (sprint) {
    sprintName.value = sprint.name;
    sprintNotes.value = sprint.notes || "";
    sprintStart.value = sprint.start.slice(0,10);
    editingId.value = sprint.id;
    document.getElementById("sprintModalTitle").textContent = "Edit Sprint";
  } else {
    sprintName.value = "";
    sprintNotes.value = "";
    sprintStart.value = new Date().toISOString().slice(0,10);
    editingId.value = "";
    document.getElementById("sprintModalTitle").textContent = "New Sprint";
  }
  modal.showModal();
  sprintName.focus();
}

/**
 * Closes the sprint modal with an animation.
 * Adds a "closing" class to the modal for 250ms, then removes it and closes the modal.
 */
export function closeSprintModal() {
  const modal = document.getElementById("sprintModal");
  modal.classList.add("closing");
  setTimeout(() => {
    modal.classList.remove("closing");
    modal.close();
  }, 250);
}


/**
 * Closes the delete modal with an animation.
 * Adds a "closing" class to the modal for 250ms, then removes it and closes the modal.
 */
export function closeDeleteModal() {
  const modal = document.getElementById("deleteModal");
  modal.classList.add("closing");
  setTimeout(() => {
    modal.classList.remove("closing");
    modal.close();
  }, 250);
}


/**
 * Formats a Date object as a string in the format "MMM d".
 * @param {Date} d - Date object to format
 * @returns {string} - Formatted date string
 */
function fmtDate(d) {
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}
