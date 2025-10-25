// iMasteryTracker – vanilla JS state + localStorage
const done = days.filter(d => d.done).length; 
const total = days.length;
function getProgressPercentage() {
return Math.round((done / total) * 100);
}


function openSprintModal(sprint) {
sprintModal.classList.add('is-opening');
sprintModal.showModal();
requestAnimationFrame(() => sprintModal.classList.remove('is-opening'));


if (sprint) {
sprintModalTitle.textContent = 'Edit Sprint';
sprintName.value = sprint.name;
sprintStart.value = sprint.start.slice(0,10);
sprintNotes.value = sprint.notes || '';
editingId.value = sprint.id;
} else {
sprintModalTitle.textContent = 'New Sprint';
sprintName.value = '';
sprintStart.valueAsDate = new Date();
sprintNotes.value = '';
editingId.value = '';
}
}


function closeDialog(dlg) {
// Graceful fade-out
dlg.classList.add('is-closing');
setTimeout(() => { dlg.close(); dlg.classList.remove('is-closing'); }, 150);
}


sprintModal.addEventListener('click', (e) => { if (e.target === sprintModal) closeDialog(sprintModal); });
confirmModal.addEventListener('click', (e) => { if (e.target === confirmModal) closeDialog(confirmModal); });


function confirmDeleteSprint(sprint) {
confirmText.textContent = `Delete sprint “${sprint.name}”? This cannot be undone.`;
confirmModal.showModal();
const onYes = () => {
state.sprints = state.sprints.filter(s => s.id !== sprint.id);
persist(); render(); confirmYes.removeEventListener('click', onYes); closeDialog(confirmModal);
};
confirmYes.addEventListener('click', onYes, { once: true });
}


function rerenderSprintInPlace(sprintId) {
// Simple strategy: full render for correctness + simplicity
render();
}


function debounce(fn, ms) {
let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}
;