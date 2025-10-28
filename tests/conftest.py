from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Iterator

import pytest
import reflex as rx
from sqlmodel import Session, SQLModel, create_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from imasterytracker.state import Habit, JournalEntry, LearningStream  # noqa: E402,F401


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.create_all(engine)

    @contextmanager
    def _session_override() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    monkeypatch.setenv("IMASTERY_SKIP_SEED", "1")
    monkeypatch.setenv("REFLEX_DB_URL", f"sqlite:///{database_path}")
    monkeypatch.setattr(rx, "session", _session_override)
    yield
