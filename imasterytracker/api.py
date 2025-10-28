from __future__ import annotations

from typing import Any, Callable, Iterable

import reflex as rx
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from sqlmodel import Session, select

from .schemas import (
    HabitCreate,
    HabitRead,
    JournalEntryCreate,
    JournalEntryRead,
    LearningStreamCreate,
    LearningStreamRead,
    WorkspaceImport,
)
from .state import DashboardState, Habit, JournalEntry, LearningStream


def _with_session(func: Callable[[Session], Any]) -> Any:
    with rx.session() as session:
        return func(session)


def _serialize(result: Iterable[Any]) -> list[dict[str, Any]]:
    return [item.model_dump() for item in result]


async def list_streams(request: Request) -> JSONResponse:  # noqa: ARG001
    data = _with_session(
        lambda session: [
            LearningStreamRead.model_validate(stream, from_attributes=True)
            for stream in session.exec(select(LearningStream))
        ]
    )
    return JSONResponse(_serialize(data), status_code=HTTP_200_OK)


async def create_stream(request: Request) -> JSONResponse:
    payload = LearningStreamCreate.model_validate(await request.json())

    def _create(session: Session) -> LearningStreamRead:
        stream = LearningStream(
            name=payload.name,
            focus=payload.focus,
            milestones_total=payload.milestones_total,
            milestones_completed=payload.milestones_completed,
            color=payload.color or DashboardState._random_color(),
        )
        session.add(stream)
        session.commit()
        session.refresh(stream)
        return LearningStreamRead.model_validate(stream, from_attributes=True)

    created = _with_session(_create)
    return JSONResponse(created.model_dump(), status_code=HTTP_201_CREATED)


async def delete_stream(request: Request) -> Response:
    stream_id = int(request.path_params.get("stream_id", 0))

    def _delete(session: Session) -> Response:
        stream = session.get(LearningStream, stream_id)
        if not stream:
            return JSONResponse({"detail": "Stream not found"}, status_code=HTTP_404_NOT_FOUND)
        session.delete(stream)
        session.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)

    return _with_session(_delete)


async def list_habits(request: Request) -> JSONResponse:  # noqa: ARG001
    data = _with_session(
        lambda session: [
            HabitRead.model_validate(habit, from_attributes=True)
            for habit in session.exec(select(Habit))
        ]
    )
    return JSONResponse(_serialize(data), status_code=HTTP_200_OK)


async def create_habit(request: Request) -> JSONResponse:
    payload = HabitCreate.model_validate(await request.json())

    def _create(session: Session) -> HabitRead:
        habit = Habit(name=payload.name, cadence=payload.cadence or "Daily", context=payload.context)
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return HabitRead.model_validate(habit, from_attributes=True)

    created = _with_session(_create)
    return JSONResponse(created.model_dump(), status_code=HTTP_201_CREATED)


async def delete_habit(request: Request) -> Response:
    habit_id = int(request.path_params.get("habit_id", 0))

    def _delete(session: Session) -> Response:
        habit = session.get(Habit, habit_id)
        if not habit:
            return JSONResponse({"detail": "Habit not found"}, status_code=HTTP_404_NOT_FOUND)
        session.delete(habit)
        session.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)

    return _with_session(_delete)


async def list_journals(request: Request) -> JSONResponse:  # noqa: ARG001
    data = _with_session(
        lambda session: [
            JournalEntryRead.model_validate(entry, from_attributes=True)
            for entry in session.exec(select(JournalEntry))
        ]
    )
    return JSONResponse(_serialize(data), status_code=HTTP_200_OK)


async def create_journal_entry(request: Request) -> JSONResponse:
    payload = JournalEntryCreate.model_validate(await request.json())

    def _create(session: Session) -> JournalEntryRead:
        entry = JournalEntry(
            title=payload.title,
            reflection=payload.reflection,
            mood=payload.mood or "Curious",
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return JournalEntryRead.model_validate(entry, from_attributes=True)

    created = _with_session(_create)
    return JSONResponse(created.model_dump(), status_code=HTTP_201_CREATED)


async def delete_journal_entry(request: Request) -> Response:
    entry_id = int(request.path_params.get("entry_id", 0))

    def _delete(session: Session) -> Response:
        entry = session.get(JournalEntry, entry_id)
        if not entry:
            return JSONResponse({"detail": "Journal entry not found"}, status_code=HTTP_404_NOT_FOUND)
        session.delete(entry)
        session.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)

    return _with_session(_delete)


async def export_workspace(request: Request) -> JSONResponse:  # noqa: ARG001
    export = DashboardState().export_workspace()
    return JSONResponse(export.model_dump(), status_code=HTTP_200_OK)


async def import_workspace(request: Request) -> JSONResponse:
    raw = await request.json()
    try:
        payload = WorkspaceImport.model_validate(raw)
    except ValidationError as error:
        details = error.errors()[0]
        raw_loc = details.get("loc", ("payload",))
        field = str(raw_loc[-1]) if raw_loc else "payload"
        field = field.replace("_", " ").title()
        message = details.get("msg", "Invalid data")
        return JSONResponse({"detail": f"{field}: {message}"}, status_code=HTTP_400_BAD_REQUEST)

    state = DashboardState()
    state.import_workspace(payload)
    if state.toast_message.startswith("Workspace imported"):
        return JSONResponse({"status": "accepted"}, status_code=HTTP_202_ACCEPTED)
    return JSONResponse({"detail": state.toast_message}, status_code=HTTP_400_BAD_REQUEST)


def register_routes(app) -> None:
    api = getattr(app, "_api", None)
    if api is None:
        raise AttributeError("Reflex app does not expose a FastAPI instance")

    api.add_route("/api/streams", list_streams, methods=["GET"])
    api.add_route("/api/streams", create_stream, methods=["POST"])
    api.add_route("/api/streams/{stream_id}", delete_stream, methods=["DELETE"])

    api.add_route("/api/habits", list_habits, methods=["GET"])
    api.add_route("/api/habits", create_habit, methods=["POST"])
    api.add_route("/api/habits/{habit_id}", delete_habit, methods=["DELETE"])

    api.add_route("/api/journals", list_journals, methods=["GET"])
    api.add_route("/api/journals", create_journal_entry, methods=["POST"])
    api.add_route("/api/journals/{entry_id}", delete_journal_entry, methods=["DELETE"])

    api.add_route("/api/export", export_workspace, methods=["GET"])
    api.add_route("/api/import", import_workspace, methods=["POST"])
