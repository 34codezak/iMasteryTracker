from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LearningStreamBase(BaseModel):
    name: str = Field(..., min_length=1)
    focus: str = ""
    milestones_total: int = Field(1, ge=1)
    milestones_completed: int = Field(0, ge=0)
    color: Optional[str] = None

    @field_validator("name", "focus", mode="before")
    def _strip_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value

    @model_validator(mode="after")
    def _cap_completed(self) -> "LearningStreamBase":
        total = self.milestones_total or 0
        completed = self.milestones_completed or 0
        self.milestones_completed = min(completed, total)
        return self


class LearningStreamCreate(LearningStreamBase):
    pass


class LearningStreamRead(LearningStreamBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HabitBase(BaseModel):
    name: str = Field(..., min_length=1)
    cadence: str = "Daily"
    context: str = ""

    @field_validator("name", "cadence", "context", mode="before")
    def _strip_habit_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value


class HabitCreate(HabitBase):
    pass


class HabitRead(HabitBase):
    id: int
    last_completed_on: Optional[dt.date] = None

    model_config = ConfigDict(from_attributes=True)


class JournalEntryBase(BaseModel):
    title: str = Field("Untitled insight", min_length=1)
    reflection: str = Field(..., min_length=1)
    mood: str = "Curious"

    @field_validator("title", "reflection", "mood", mode="before")
    def _strip_journal_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryRead(JournalEntryBase):
    id: int
    created_at: Optional[dt.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceImport(BaseModel):
    streams: List[LearningStreamCreate] = Field(default_factory=list)
    habits: List[HabitCreate] = Field(default_factory=list)
    journal_entries: List[JournalEntryCreate] = Field(default_factory=list)


class WorkspaceExport(BaseModel):
    streams: List[LearningStreamRead]
    habits: List[HabitRead]
    journal_entries: List[JournalEntryRead]
