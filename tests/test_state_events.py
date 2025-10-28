from __future__ import annotations

import pytest
import reflex as rx
from sqlmodel import Session, select

from imasterytracker.state import DashboardState, Habit, JournalEntry, LearningStream


def _get_single(session: Session, model):
    results = list(session.exec(select(model)))
    assert len(results) == 1
    return results[0]


def test_add_stream_creates_record():
    state = DashboardState()
    state.stream_name = "Deep Practice"
    state.stream_focus = "Deliberate Kotlin drills"
    state.stream_milestones_total = "5"
    state.stream_milestones_completed = "2"

    state.add_stream()

    assert state.toast_message == "New learning stream added."
    with rx.session() as session:
        stream = _get_single(session, LearningStream)
        assert stream.name == "Deep Practice"
        assert stream.milestones_completed == 2
        assert stream.milestones_total == 5


def test_add_stream_with_invalid_numbers_sets_error():
    state = DashboardState()
    state.stream_name = ""
    state.stream_milestones_total = "-1"

    state.add_stream()

    assert "Name" in state.toast_message


def test_habit_toggle_updates_last_completed(monkeypatch):
    state = DashboardState()
    state.habit_name = "Daily review"
    state.habit_cadence = "Daily"
    state.habit_context = ""

    state.add_habit()
    with rx.session() as session:
        habit = _get_single(session, Habit)
        assert habit.last_completed_on is None
        habit_id = habit.id

    state.toggle_habit(habit_id)
    with rx.session() as session:
        habit = session.get(Habit, habit_id)
        assert habit.last_completed_on is not None


def test_add_journal_requires_reflection():
    state = DashboardState()
    state.journal_title = ""
    state.journal_reflection = "  "

    state.add_journal_entry()

    assert "Reflection" in state.toast_message


def test_import_and_export_round_trip():
    state = DashboardState()
    workspace = {
        "streams": [
            {
                "name": "ML Systems",
                "focus": "ship a retriever",
                "milestones_total": 3,
                "milestones_completed": 1,
                "color": "#123456",
            }
        ],
        "habits": [
            {"name": "Ship notes", "cadence": "Daily", "context": ""}
        ],
        "journal_entries": [
            {"title": "Learned", "reflection": "Vectors", "mood": "Curious"}
        ],
    }

    state.import_workspace(workspace)
    exported = state.export_workspace()

    assert exported.streams[0].name == "ML Systems"
    assert exported.habits[0].name == "Ship notes"
    assert exported.journal_entries[0].title == "Learned"
