from __future__ import annotations

import datetime as dt
import os
import random
from typing import List

import reflex as rx
from pydantic import ValidationError
from sqlmodel import Field, select

from rxconfig import config as app_config

from .schemas import (
    HabitCreate,
    HabitRead,
    JournalEntryCreate,
    JournalEntryRead,
    LearningStreamCreate,
    LearningStreamRead,
    WorkspaceExport,
    WorkspaceImport,
)


COLOR_PALETTE = [
    "#6366F1",
    "#22C55E",
    "#F97316",
    "#EC4899",
    "#0EA5E9",
    "#FACC15",
]


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class LearningStream(rx.Model, table=True):
    """A deliberate practice focus area."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    focus: str = ""
    milestones_total: int = 1
    milestones_completed: int = 0
    color: str = "#6366F1"
    created_at: dt.datetime = Field(default_factory=_utcnow, nullable=False)


class Habit(rx.Model, table=True):
    """A daily or weekly ritual that supports growth."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    cadence: str = "Daily"
    context: str = ""
    last_completed_on: dt.date | None = Field(default=None, nullable=True)
    created_at: dt.datetime = Field(default_factory=_utcnow, nullable=False)


class JournalEntry(rx.Model, table=True):
    """Short reflections documenting insights."""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    reflection: str
    mood: str = "Curious"
    created_at: dt.datetime = Field(default_factory=_utcnow, nullable=False)


class DashboardState(rx.State):
    """Main application state for the iMastery dashboard."""

    show_stream_modal: bool = False
    show_habit_modal: bool = False
    show_journal_modal: bool = False

    stream_name: str = ""
    stream_focus: str = ""
    stream_milestones_total: str = "6"
    stream_milestones_completed: str = "0"

    habit_name: str = ""
    habit_cadence: str = "Daily"
    habit_context: str = ""

    journal_title: str = ""
    journal_reflection: str = ""
    journal_mood: str = "Curious"

    toast_message: str = ""

    async def init(self):
        await super().init()
        LearningStream.create_all()
        Habit.create_all()
        JournalEntry.create_all()
        self._seed_defaults()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _random_color() -> str:
        return random.choice(COLOR_PALETTE)

    @staticmethod
    def _today() -> dt.date:
        return dt.date.today()

    def _seed_defaults(self) -> None:
        if app_config.env == "prod" or os.getenv("IMASTERY_SKIP_SEED") == "1":
            return

        with rx.session() as session:
            if not session.exec(select(LearningStream)).first():
                session.add_all(
                    [
                        LearningStream(
                            name="AI Engineering",
                            focus="Ship a conversational AI mentor that personalises study sprints.",
                            milestones_total=6,
                            milestones_completed=4,
                            color="#6366F1",
                        ),
                        LearningStream(
                            name="Product Strategy",
                            focus="Run weekly experiments to tighten the build-measure-learn loop.",
                            milestones_total=5,
                            milestones_completed=2,
                            color="#22C55E",
                        ),
                    ]
                )
            if not session.exec(select(Habit)).first():
                session.add_all(
                    [
                        Habit(
                            name="Deep Work Block",
                            cadence="Daily",
                            context="90 minutes of focused creation before meetings.",
                            last_completed_on=self._today(),
                        ),
                        Habit(
                            name="Knowledge Capture",
                            cadence="Daily",
                            context="Summarise the top learning insight in the vault.",
                        ),
                    ]
                )
            if not session.exec(select(JournalEntry)).first():
                session.add_all(
                    [
                        JournalEntry(
                            title="Synthesised a practice loop",
                            reflection="Mapped how research notes flow into prototypes and user feedback.",
                            mood="Energised",
                        ),
                        JournalEntry(
                            title="Reframed blockers",
                            reflection="Used the five whys to unblock the onboarding flow redesign.",
                            mood="Curious",
                        ),
                    ]
                )
            session.commit()

    # ------------------------------------------------------------------
    # Database accessors
    # ------------------------------------------------------------------
    def _get_streams(self) -> List[LearningStream]:
        with rx.session() as session:
            return list(
                session.exec(
                    select(LearningStream).order_by(LearningStream.created_at.desc())
                )
            )

    def _get_habits(self) -> List[Habit]:
        with rx.session() as session:
            return list(
                session.exec(select(Habit).order_by(Habit.created_at.desc()))
            )

    def _get_journals(self) -> List[JournalEntry]:
        with rx.session() as session:
            return list(
                session.exec(
                    select(JournalEntry).order_by(JournalEntry.created_at.desc())
                )
            )

    @rx.var
    def streams(self) -> List[LearningStream]:
        return self._get_streams()

    @rx.var
    def habits(self) -> List[Habit]:
        return self._get_habits()

    @rx.var
    def journal_entries(self) -> List[JournalEntry]:
        return self._get_journals()

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    @rx.var
    def total_streams(self) -> int:
        return len(self._get_streams())

    @rx.var
    def milestone_completion(self) -> int:
        streams = self._get_streams()
        total = sum(stream.milestones_total for stream in streams)
        completed = sum(stream.milestones_completed for stream in streams)
        if total == 0:
            return 0
        return round((completed / total) * 100)

    @rx.var
    def total_habits(self) -> int:
        return len(self._get_habits())

    @rx.var
    def milestone_copy(self) -> str:
        streams = self._get_streams()
        completed = sum(stream.milestones_completed for stream in streams)
        total = sum(stream.milestones_total for stream in streams)
        return f"{completed:02}/{total:02}" if total else "00/00"

    @rx.var
    def habits_completed_today(self) -> int:
        today = self._today()
        return sum(1 for habit in self._get_habits() if habit.last_completed_on == today)

    @rx.var
    def milestone_detail(self) -> str:
        return f"Secured milestones {self.milestone_copy}"

    @rx.var
    def journal_count(self) -> int:
        return len(self._get_journals())

    @rx.var
    def reflections_this_week(self) -> int:
        seven_days_ago = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
        return sum(1 for entry in self._get_journals() if entry.created_at >= seven_days_ago)

    @rx.var
    def habit_consistency_copy(self) -> str:
        habits = self._get_habits()
        if not habits:
            return "Create a ritual to build your execution rhythm."
        completed = sum(1 for habit in habits if habit.last_completed_on == self._today())
        return f"{completed} of {len(habits)} rituals logged today"

    @rx.var
    def next_stream_message(self) -> str:
        streams = sorted(self._get_streams(), key=lambda stream: stream.created_at)
        for stream in streams:
            if stream.milestones_completed < stream.milestones_total:
                remaining = stream.milestones_total - stream.milestones_completed
                label = "milestone" if remaining == 1 else "milestones"
                return f"{stream.name}: {remaining} {label} to go"
        return "All learning streams are fully complete."

    @rx.var
    def milestone_trend_message(self) -> str:
        completion = self.milestone_completion
        if completion >= 75:
            return "Momentum is compounding—keep shipping!"
        if completion >= 40:
            return "Solid traction. Review blockers to accelerate."
        if completion > 0:
            return "Early progress logged—lean into the next milestone."
        return "Set your first milestone to start tracking mastery."

    @rx.var
    def latest_journal_title(self) -> str:
        entries = self._get_journals()
        if not entries:
            return "No reflections yet"
        return entries[0].title

    @rx.var
    def latest_journal_preview(self) -> str:
        entries = self._get_journals()
        if not entries:
            return "Capture your latest insight to build your mastery journal."
        text = entries[0].reflection.strip()
        if len(text) <= 140:
            return text
        return text[:137].rstrip() + "..."

    @rx.var
    def streams_active_count(self) -> int:
        return sum(1 for stream in self._get_streams() if stream.milestones_completed < stream.milestones_total)

    # ------------------------------------------------------------------
    # Stream events
    # ------------------------------------------------------------------
    def open_stream_modal(self):
        self.show_stream_modal = True

    def close_stream_modal(self):
        self.show_stream_modal = False
        self.stream_name = ""
        self.stream_focus = ""
        self.stream_milestones_total = "6"
        self.stream_milestones_completed = "0"

    def add_stream(self):
        try:
            payload = LearningStreamCreate(
                name=self.stream_name,
                focus=self.stream_focus,
                milestones_total=self.stream_milestones_total,
                milestones_completed=self.stream_milestones_completed,
            )
        except ValidationError as error:
            self.toast_message = self._format_validation_error(error)
            return

        with rx.session() as session:
            stream = LearningStream(
                name=payload.name,
                focus=payload.focus,
                milestones_total=payload.milestones_total,
                milestones_completed=payload.milestones_completed,
                color=payload.color or self._random_color(),
            )
            session.add(stream)
            session.commit()
        self.close_stream_modal()
        self.toast_message = "New learning stream added."

    def update_stream_progress(self, stream_id: int, delta: int):
        with rx.session() as session:
            stream = session.get(LearningStream, stream_id)
            if not stream:
                return
            stream.milestones_completed = min(
                stream.milestones_total,
                max(0, stream.milestones_completed + delta),
            )
            session.add(stream)
            session.commit()
        self.toast_message = "Progress updated."

    def remove_stream(self, stream_id: int):
        with rx.session() as session:
            stream = session.get(LearningStream, stream_id)
            if not stream:
                return
            session.delete(stream)
            session.commit()
        self.toast_message = "Stream removed."

    # ------------------------------------------------------------------
    # Habit events
    # ------------------------------------------------------------------
    def open_habit_modal(self):
        self.show_habit_modal = True

    def close_habit_modal(self):
        self.show_habit_modal = False
        self.habit_name = ""
        self.habit_cadence = "Daily"
        self.habit_context = ""

    def add_habit(self):
        try:
            payload = HabitCreate(
                name=self.habit_name,
                cadence=self.habit_cadence,
                context=self.habit_context,
            )
        except ValidationError as error:
            self.toast_message = self._format_validation_error(error)
            return

        with rx.session() as session:
            habit = Habit(
                name=payload.name,
                cadence=payload.cadence or "Daily",
                context=payload.context,
            )
            session.add(habit)
            session.commit()
        self.close_habit_modal()
        self.toast_message = "Habit added."

    def toggle_habit(self, habit_id: int):
        today = self._today()
        with rx.session() as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                return
            if habit.last_completed_on == today:
                habit.last_completed_on = None
            else:
                habit.last_completed_on = today
            session.add(habit)
            session.commit()
        self.toast_message = "Habit check-in updated."

    def remove_habit(self, habit_id: int):
        with rx.session() as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                return
            session.delete(habit)
            session.commit()
        self.toast_message = "Habit removed."

    # ------------------------------------------------------------------
    # Journal events
    # ------------------------------------------------------------------
    def open_journal_modal(self):
        self.show_journal_modal = True

    def close_journal_modal(self):
        self.show_journal_modal = False
        self.journal_title = ""
        self.journal_reflection = ""
        self.journal_mood = "Curious"

    def add_journal_entry(self):
        try:
            payload = JournalEntryCreate(
                title=self.journal_title or "Untitled insight",
                reflection=self.journal_reflection,
                mood=self.journal_mood,
            )
        except ValidationError as error:
            self.toast_message = self._format_validation_error(error)
            return

        with rx.session() as session:
            entry = JournalEntry(
                title=payload.title,
                reflection=payload.reflection,
                mood=payload.mood or "Curious",
            )
            session.add(entry)
            session.commit()
        self.close_journal_modal()
        self.toast_message = "Reflection captured."

    def import_workspace(self, data: WorkspaceImport | dict):
        try:
            payload = (
                data if isinstance(data, WorkspaceImport) else WorkspaceImport.model_validate(data)
            )
        except ValidationError as error:
            self.toast_message = self._format_validation_error(error)
            return

        self._replace_workspace(payload)
        self.toast_message = "Workspace imported successfully."

    def _replace_workspace(self, payload: WorkspaceImport) -> None:
        with rx.session() as session:
            for model in (LearningStream, Habit, JournalEntry):
                for record in session.exec(select(model)):
                    session.delete(record)
            session.commit()

            for stream in payload.streams:
                session.add(
                    LearningStream(
                        name=stream.name,
                        focus=stream.focus,
                        milestones_total=stream.milestones_total,
                        milestones_completed=stream.milestones_completed,
                        color=stream.color or self._random_color(),
                    )
                )
            for habit in payload.habits:
                session.add(
                    Habit(
                        name=habit.name,
                        cadence=habit.cadence or "Daily",
                        context=habit.context,
                    )
                )
            for entry in payload.journal_entries:
                session.add(
                    JournalEntry(
                        title=entry.title,
                        reflection=entry.reflection,
                        mood=entry.mood or "Curious",
                    )
                )
            session.commit()

    def export_workspace(self) -> WorkspaceExport:
        with rx.session() as session:
            streams = [
                LearningStreamRead.model_validate(stream, from_attributes=True)
                for stream in session.exec(select(LearningStream))
            ]
            habits = [
                HabitRead.model_validate(habit, from_attributes=True)
                for habit in session.exec(select(Habit))
            ]
            journal_entries = [
                JournalEntryRead.model_validate(entry, from_attributes=True)
                for entry in session.exec(select(JournalEntry))
            ]

        return WorkspaceExport(
            streams=streams,
            habits=habits,
            journal_entries=journal_entries,
        )

    def remove_journal_entry(self, journal_id: int):
        with rx.session() as session:
            entry = session.get(JournalEntry, journal_id)
            if not entry:
                return
            session.delete(entry)
            session.commit()
        self.toast_message = "Entry removed."

    def clear_toast(self):
        self.toast_message = ""

    def _format_validation_error(self, error: ValidationError) -> str:
        first = error.errors()[0]
        field = first.get("loc", ["value"])[0]
        msg = first.get("msg", "Invalid data")
        return f"{str(field).replace('_', ' ').capitalize()}: {msg}."
