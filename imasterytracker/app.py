from __future__ import annotations

import datetime as dt

import reflex as rx

from .state import DashboardState, Habit, JournalEntry, LearningStream


def metric_card(icon: str, label: str, value: rx.Component, helper: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=22),
                rx.text(label, size="3", weight="medium", color="gray.11"),
                justify="between",
                width="100%",
                align="center",
            ),
            value,
            rx.text(helper, size="2", color="gray.9"),
            gap="2",
            align="start",
        ),
        variant="surface",
        padding="5",
        min_height="120px",
        width="100%",
    )


def stream_card(stream: LearningStream) -> rx.Component:
    progress = (
        int((stream.milestones_completed / stream.milestones_total) * 100)
        if stream.milestones_total
        else 0
    )
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(f"{stream.milestones_total} planned", color_scheme="gray"),
                rx.spacer(),
                rx.button(
                    rx.icon("trash-2"),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=lambda: DashboardState.remove_stream(stream.id),
                ),
            ),
            rx.heading(stream.name, size="6"),
            rx.text(stream.focus or "", color="gray.9", size="3"),
            rx.progress(value=progress, max=100, color_scheme="purple"),
            rx.hstack(
                rx.badge(
                    f"{stream.milestones_completed} milestones", color_scheme="purple"
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("plus"),
                    size="2",
                    variant="solid",
                    color_scheme="purple",
                    on_click=lambda: DashboardState.update_stream_progress(
                        stream.id, 1
                    ),
                ),
                rx.button(
                    rx.icon("minus"),
                    size="2",
                    variant="soft",
                    color_scheme="purple",
                    on_click=lambda: DashboardState.update_stream_progress(
                        stream.id, -1
                    ),
                ),
            ),
            gap="3",
            align="start",
        ),
        style={
            "border_top": f"5px solid {stream.color}",
        },
        padding="5",
        width="100%",
    )


def habit_card(habit: Habit) -> rx.Component:
    is_complete = habit.last_completed_on == dt.date.today()
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("alarm-clock", size=18),
                rx.heading(habit.name, size="4"),
                rx.spacer(),
                rx.button(
                    rx.icon("trash-2"),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=lambda: DashboardState.remove_habit(habit.id),
                ),
            ),
            rx.text(habit.context or "", size="2", color="gray.9"),
            rx.hstack(
                rx.badge(habit.cadence, color_scheme="cyan"),
                rx.spacer(),
                rx.switch(
                    is_checked=is_complete,
                    on_change=lambda _: DashboardState.toggle_habit(habit.id),
                    color_scheme="cyan",
                ),
            ),
            gap="3",
            align="start",
        ),
        padding="4",
    )


def journal_card(entry: JournalEntry) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(entry.title, size="4"),
                rx.spacer(),
                rx.badge(entry.mood, color_scheme="pink"),
                rx.button(
                    rx.icon("trash-2"),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=lambda: DashboardState.remove_journal_entry(entry.id),
                ),
            ),
            rx.text(entry.reflection, size="3", color="gray.9"),
            rx.text(
                entry.created_at.strftime("%b %d, %Y"),
                size="2",
                color="gray.8",
            ),
            gap="3",
            align="start",
        ),
        padding="4",
    )


def modal_container(is_open, content: rx.Component) -> rx.Component:
    return rx.cond(
        is_open,
        rx.center(
            content,
            position="fixed",
            top="0",
            left="0",
            right="0",
            bottom="0",
            background_color="rgba(15, 23, 42, 0.72)",
            padding="6",
            z_index="50",
        ),
    )


def stream_modal() -> rx.Component:
    return modal_container(
        DashboardState.show_stream_modal,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Create learning stream", size="6"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x"),
                        variant="ghost",
                        on_click=DashboardState.close_stream_modal,
                    ),
                ),
                rx.vstack(
                    rx.text("Name", size="2", color="gray.9"),
                    rx.input(
                        placeholder="e.g. Systems Design Mastery",
                        value=DashboardState.stream_name,
                        on_change=DashboardState.set_stream_name,
                    ),
                    gap="2",
                ),
                rx.vstack(
                    rx.text("Focus narrative", size="2", color="gray.9"),
                    rx.textarea(
                        placeholder="What makes this stream matter?",
                        value=DashboardState.stream_focus,
                        on_change=DashboardState.set_stream_focus,
                        min_height="120px",
                    ),
                    gap="2",
                ),
                rx.flex(
                    rx.vstack(
                        rx.text("Milestones planned", size="2"),
                        rx.input(
                            type_="number",
                            min_="1",
                            value=DashboardState.stream_milestones_total,
                            on_change=DashboardState.set_stream_milestones_total,
                        ),
                        gap="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Milestones complete", size="2"),
                        rx.input(
                            type_="number",
                            min_="0",
                            value=DashboardState.stream_milestones_completed,
                            on_change=DashboardState.set_stream_milestones_completed,
                        ),
                        gap="2",
                        width="100%",
                    ),
                    gap="4",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        "Create stream",
                        on_click=DashboardState.add_stream,
                        variant="solid",
                        color_scheme="purple",
                    ),
                    rx.button(
                        "Cancel",
                        on_click=DashboardState.close_stream_modal,
                        variant="soft",
                    ),
                    justify="end",
                    width="100%",
                    gap="3",
                ),
                gap="4",
                width="480px",
            ),
            padding="6",
        ),
    )


def habit_modal() -> rx.Component:
    return modal_container(
        DashboardState.show_habit_modal,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Add ritual", size="6"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x"),
                        variant="ghost",
                        on_click=DashboardState.close_habit_modal,
                    ),
                ),
                rx.vstack(
                    rx.text("Habit name", size="2", color="gray.9"),
                    rx.input(
                        placeholder="e.g. Evening Retrospective",
                        value=DashboardState.habit_name,
                        on_change=DashboardState.set_habit_name,
                    ),
                    gap="2",
                ),
                rx.flex(
                    rx.vstack(
                        rx.text("Cadence", size="2", color="gray.9"),
                        rx.select(
                            ["Daily", "Weekly", "Bi-weekly"],
                            value=DashboardState.habit_cadence,
                            on_change=DashboardState.set_habit_cadence,
                        ),
                        gap="2",
                        width="100%",
                    ),
                    gap="4",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Context", size="2", color="gray.9"),
                    rx.textarea(
                        placeholder="Where does this habit happen?",
                        value=DashboardState.habit_context,
                        on_change=DashboardState.set_habit_context,
                        min_height="100px",
                    ),
                    gap="2",
                ),
                rx.hstack(
                    rx.button(
                        "Save habit",
                        on_click=DashboardState.add_habit,
                        color_scheme="cyan",
                    ),
                    rx.button(
                        "Cancel",
                        on_click=DashboardState.close_habit_modal,
                        variant="soft",
                    ),
                    justify="end",
                    gap="3",
                    width="100%",
                ),
                gap="4",
                width="420px",
            ),
            padding="6",
        ),
    )


def journal_modal() -> rx.Component:
    return modal_container(
        DashboardState.show_journal_modal,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Capture reflection", size="6"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x"),
                        variant="ghost",
                        on_click=DashboardState.close_journal_modal,
                    ),
                ),
                rx.vstack(
                    rx.text("Title", size="2", color="gray.9"),
                    rx.input(
                        placeholder="What did you learn?",
                        value=DashboardState.journal_title,
                        on_change=DashboardState.set_journal_title,
                    ),
                    gap="2",
                ),
                rx.flex(
                    rx.vstack(
                        rx.text("Mood", size="2", color="gray.9"),
                        rx.select(
                            ["Curious", "Energised", "Calm", "Reflective"],
                            value=DashboardState.journal_mood,
                            on_change=DashboardState.set_journal_mood,
                        ),
                        gap="2",
                        width="100%",
                    ),
                    gap="4",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Reflection", size="2", color="gray.9"),
                    rx.textarea(
                        placeholder="Capture insights, experiments, and adjustments...",
                        value=DashboardState.journal_reflection,
                        on_change=DashboardState.set_journal_reflection,
                        min_height="160px",
                    ),
                    gap="2",
                ),
                rx.hstack(
                    rx.button(
                        "Log entry",
                        on_click=DashboardState.add_journal_entry,
                        color_scheme="pink",
                    ),
                    rx.button(
                        "Cancel",
                        on_click=DashboardState.close_journal_modal,
                        variant="soft",
                    ),
                    justify="end",
                    gap="3",
                    width="100%",
                ),
                gap="4",
                width="520px",
            ),
            padding="6",
        ),
    )


def dashboard_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("brain", size=26),
                    rx.heading("iMastery Tracker", size="8"),
                    align="center",
                    gap="3",
                ),
                rx.spacer(),
                rx.button(
                    "New stream",
                    on_click=DashboardState.open_stream_modal,
                    color_scheme="purple",
                ),
                rx.button(
                    "Add ritual",
                    on_click=DashboardState.open_habit_modal,
                    variant="soft",
                    color_scheme="cyan",
                ),
                rx.button(
                    "Journal entry",
                    on_click=DashboardState.open_journal_modal,
                    variant="soft",
                    color_scheme="pink",
                ),
                width="100%",
                align="center",
                gap="3",
            ),
            rx.text(
                "Design deliberate practice loops, track signals, and celebrate forward motion.",
                size="3",
                color="gray.9",
            ),
            rx.cond(
                DashboardState.toast_message,
                rx.card(
                    rx.hstack(
                        rx.text(DashboardState.toast_message),
                        rx.spacer(),
                        rx.button(
                            rx.icon("x"),
                            size="1",
                            variant="ghost",
                            on_click=DashboardState.clear_toast,
                        ),
                    ),
                    padding="4",
                    background="mint.3",
                ),
            ),
            rx.grid(
                metric_card(
                    "radix-icons:mixer-horizontal",
                    "Learning streams",
                    rx.heading(DashboardState.total_streams, size="8", weight="bold"),
                    "Active areas of focused growth",
                ),
                metric_card(
                    "radix-icons:target",
                    "Milestone completion",
                    rx.hstack(
                        rx.heading(DashboardState.milestone_completion, size="8", weight="bold"),
                        rx.text("%", size="4", color="gray.9"),
                        align="baseline",
                        gap="2",
                    ),
                    DashboardState.milestone_detail,
                ),
                metric_card(
                    "radix-icons:activity-log",
                    "Rituals completed",
                    rx.heading(DashboardState.habits_completed_today, size="8", weight="bold"),
                    "Check-ins logged today",
                ),
                metric_card(
                    "radix-icons:notebook",
                    "Reflection entries",
                    rx.heading(DashboardState.journal_count, size="8", weight="bold"),
                    "Documented insights",
                ),
                columns={"base": 1, "md": 2, "lg": 4},
                gap="4",
                width="100%",
            ),
            rx.flex(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Learning streams", size="6"),
                            rx.spacer(),
                            rx.button(
                                "New",
                                size="2",
                                on_click=DashboardState.open_stream_modal,
                                color_scheme="purple",
                            ),
                        ),
                        rx.grid(
                            rx.foreach(
                                DashboardState.streams,
                                lambda stream: stream_card(stream),
                            ),
                            columns={"base": 1, "md": 2},
                            gap="4",
                            width="100%",
                        ),
                        gap="4",
                    ),
                    padding="5",
                    width="100%",
                ),
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Daily rituals", size="6"),
                                rx.badge(
                                    "Discipline compounds",
                                    color_scheme="cyan",
                                    variant="soft",
                                ),
                                rx.spacer(),
                                rx.button(
                                    "Add",
                                    size="2",
                                    variant="ghost",
                                    on_click=DashboardState.open_habit_modal,
                                ),
                            ),
                            rx.vstack(
                                rx.foreach(
                                    DashboardState.habits,
                                    lambda habit: habit_card(habit),
                                ),
                                gap="3",
                                width="100%",
                            ),
                            gap="4",
                        ),
                        padding="5",
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Reflection log", size="6"),
                                rx.spacer(),
                                rx.button(
                                    "New entry",
                                    size="2",
                                    variant="ghost",
                                    on_click=DashboardState.open_journal_modal,
                                ),
                            ),
                            rx.vstack(
                                rx.foreach(
                                    DashboardState.journal_entries,
                                    lambda entry: journal_card(entry),
                                ),
                                gap="3",
                                width="100%",
                            ),
                            gap="4",
                        ),
                        padding="5",
                        width="100%",
                    ),
                    gap="5",
                    width="40%",
                ),
                gap="5",
                width="100%",
                direction={"base": "column", "lg": "row"},
            ),
            stream_modal(),
            habit_modal(),
            journal_modal(),
            gap="6",
            padding_y="8",
            width="100%",
        ),
        max_width="1200px",
        margin_x="auto",
        padding_x={"base": "4", "lg": "8"},
        padding_y="10",
    )


app = rx.App(
    theme=rx.theme(appearance="dark", has_background=True),
    stylesheets=[
        "https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap",
    ],
    style={"font_family": "'General Sans', sans-serif"},
)
app.add_page(dashboard_page, route="/", title="iMastery Tracker Dashboard", on_load=DashboardState.clear_toast)
# app.compile()
