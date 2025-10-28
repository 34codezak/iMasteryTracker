from __future__ import annotations

import datetime as dt
from collections.abc import Callable

import reflex as rx

from .state import DashboardState, Habit, JournalEntry, LearningStream


def metric_card(
    icon: str,
    label: str,
    value: rx.Component,
    helper: str,
    accent: str = "var(--accent-9)",
) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=20, color=accent),
                    background_color="rgba(148, 163, 184, 0.08)",
                    padding="2",
                    border_radius="full",
                ),
                rx.spacer(),
                rx.badge("This week", color_scheme="gray", variant="soft"),
                align="center",
                width="100%",
            ),
            rx.vstack(
                rx.text(label, size="2", color="gray.9", weight="medium"),
                value,
                gap="1",
                align="start",
            ),
            rx.divider(margin_y="2"),
            rx.text(helper, size="2", color="gray.9"),
            gap="3",
            align="start",
        ),
        variant="surface",
        padding="5",
        min_height="140px",
        width="100%",
        background="linear-gradient(135deg, rgba(15,23,42,0.85), rgba(30,41,59,0.92))",
        border="1px solid rgba(148, 163, 184, 0.12)",
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
                rx.badge(
                    f"{stream.milestones_total} planned", color_scheme="gray", variant="soft"
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("trash-2"),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=lambda: DashboardState.remove_stream(stream.id),
                ),
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(stream.name, size="6"),
                    rx.spacer(),
                    rx.badge(
                        f"{progress}%", color_scheme="purple", variant="solid"
                    ),
                ),
                rx.text(stream.focus or "", color="gray.9", size="3"),
                gap="2",
                align="start",
            ),
            rx.progress(value=progress, max=100, color_scheme="purple"),
            rx.hstack(
                rx.badge(
                    f"{stream.milestones_completed} complete", color_scheme="purple"
                ),
                rx.text(
                    f"{max(stream.milestones_total - stream.milestones_completed, 0)} remaining",
                    size="2",
                    color="gray.9",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("minus"),
                    size="2",
                    variant="soft",
                    color_scheme="purple",
                    on_click=lambda: DashboardState.update_stream_progress(
                        stream.id, -1
                    ),
                ),
                rx.button(
                    rx.icon("plus"),
                    size="2",
                    variant="solid",
                    color_scheme="purple",
                    on_click=lambda: DashboardState.update_stream_progress(
                        stream.id, 1
                    ),
                ),
            ),
            gap="4",
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
                rx.icon("alarm-clock", size=18, color="var(--cyan-9)"),
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
                rx.badge(habit.cadence, color_scheme="cyan", variant="soft"),
                rx.spacer(),
                rx.switch(
                    is_checked=is_complete,
                    on_change=lambda _: DashboardState.toggle_habit(habit.id),
                    color_scheme="cyan",
                ),
            ),
            rx.cond(
                is_complete,
                rx.badge("Logged today", color_scheme="cyan", variant="surface"),
                rx.text("Tap the switch once you've honoured the ritual.", size="2", color="gray.8"),
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
            rx.text(
                entry.reflection,
                size="2",
                color="gray.9",
                line_height="1.6",
            ),
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


def empty_state(
    message: str,
    action_label: str | None = None,
    action: Callable[[], None] | None = None,
) -> rx.Component:
    controls: list[rx.Component] = []
    if action_label and action is not None:
        controls.append(
            rx.button(
                action_label,
                on_click=action,
                variant="soft",
                color_scheme="purple",
                size="2",
            )
        )
    return rx.center(
        rx.vstack(
            rx.icon("star", size=28, color="var(--gray-11)"),
            rx.text(message, size="2", color="gray.9", align="center"),
            *controls,
            gap="3",
            align="center",
        ),
        min_height="140px",
        border="1px dashed rgba(148, 163, 184, 0.24)",
        border_radius="12px",
        padding="6",
        background_color="rgba(15, 23, 42, 0.35)",
    )


def streams_section() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Learning streams", size="6"),
                rx.spacer(),
                rx.badge(
                    DashboardState.milestone_trend_message,
                    color_scheme="purple",
                    variant="soft",
                ),
                rx.button(
                    "New",
                    size="2",
                    on_click=DashboardState.open_stream_modal,
                    color_scheme="purple",
                ),
            ),
            rx.text(
                "Focus areas that drive meaningful practice loops.",
                size="2",
                color="gray.9",
            ),
            rx.cond(
                DashboardState.total_streams > 0,
                rx.grid(
                    rx.foreach(
                        DashboardState.streams,
                        lambda stream: stream_card(stream),
                    ),
                    columns={"base": 1, "md": 2},
                    gap="4",
                    width="100%",
                ),
                empty_state(
                    "Design your first learning stream to anchor deliberate practice.",
                    "Create stream",
                    DashboardState.open_stream_modal,
                ),
            ),
            gap="4",
            align="start",
        ),
        padding="5",
        width="100%",
    )


def habits_section() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Daily rituals", size="6"),
                rx.spacer(),
                rx.badge(
                    DashboardState.habit_consistency_copy,
                    color_scheme="cyan",
                    variant="soft",
                ),
                rx.button(
                    "Add",
                    size="2",
                    variant="soft",
                    on_click=DashboardState.open_habit_modal,
                    color_scheme="cyan",
                ),
            ),
            rx.text(
                "Micro commitments that compound focus and execution.",
                size="2",
                color="gray.9",
            ),
            rx.cond(
                DashboardState.total_habits > 0,
                rx.vstack(
                    rx.foreach(
                        DashboardState.habits,
                        lambda habit: habit_card(habit),
                    ),
                    gap="3",
                    width="100%",
                ),
                empty_state(
                    "Add your first ritual to lock in a supportive rhythm.",
                    "Add ritual",
                    DashboardState.open_habit_modal,
                ),
            ),
            gap="4",
            align="start",
        ),
        padding="5",
        width="100%",
    )


def journal_section() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Reflection log", size="6"),
                rx.spacer(),
                rx.badge(
                    rx.hstack(
                        rx.icon("book-open", size=14),
                        rx.text(DashboardState.journal_count, weight="medium"),
                        rx.text("entries", size="2"),
                        align="center",
                        gap="2",
                    ),
                    color_scheme="pink",
                    variant="soft",
                ),
                rx.button(
                    "New entry",
                    size="2",
                    variant="soft",
                    on_click=DashboardState.open_journal_modal,
                    color_scheme="pink",
                ),
            ),
            rx.text(
                "Capture insights, retrospectives, and growth inflection points.",
                size="2",
                color="gray.9",
            ),
            rx.cond(
                DashboardState.journal_count > 0,
                rx.vstack(
                    rx.foreach(
                        DashboardState.journal_entries,
                        lambda entry: journal_card(entry),
                    ),
                    gap="3",
                    width="100%",
                ),
                empty_state(
                    "Log your first reflection to chronicle the mastery journey.",
                    "Journal entry",
                    DashboardState.open_journal_modal,
                ),
            ),
            gap="4",
            align="start",
        ),
        padding="5",
        width="100%",
    )


def momentum_insights() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("activity", size=20, color="var(--purple-9)"),
                rx.heading("Momentum pulse", size="5"),
                rx.spacer(),
                rx.badge(
                    rx.hstack(
                        rx.icon("calendar", size=14),
                        rx.text(DashboardState.reflections_this_week, weight="medium"),
                        rx.text("reflections this week", size="2"),
                        align="center",
                        gap="2",
                    ),
                    color_scheme="purple",
                    variant="surface",
                ),
            ),
            rx.text(
                "A quick read on how your practice engine is performing.",
                size="2",
                color="gray.9",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("target", size=16, color="var(--purple-9)"),
                    rx.text(DashboardState.next_stream_message, size="2", color="gray.9"),
                    align="center",
                    gap="2",
                ),
                rx.hstack(
                    rx.icon("clock", size=16, color="var(--cyan-9)"),
                    rx.text(DashboardState.habit_consistency_copy, size="2", color="gray.9"),
                    align="center",
                    gap="2",
                ),
                rx.hstack(
                    rx.icon("star", size=16, color="var(--pink-9)"),
                    rx.text(DashboardState.latest_journal_title, size="2", color="gray.9"),
                    align="center",
                    gap="2",
                ),
                rx.text(DashboardState.latest_journal_preview, size="2", color="gray.8"),
                gap="3",
                align="start",
            ),
            gap="4",
            align="start",
        ),
        padding="5",
        width="100%",
    )


def practice_playbooks() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("notebook", size=20, color="var(--gray-11)"),
                rx.heading("Practice playbooks", size="5"),
                rx.spacer(),
            ),
            rx.text(
                "Quick prompts to help you shape impactful iterations.",
                size="2",
                color="gray.9",
            ),
            rx.accordion.root(
                rx.accordion.item(
                    rx.accordion.trigger("Weekly runway"),
                    rx.accordion.content(
                        rx.text(
                            "Clarify the 1-2 milestones that unlock the biggest learning delta this week.",
                            size="2",
                            color="gray.9",
                        )
                    ),
                    value="runway",
                ),
                rx.accordion.item(
                    rx.accordion.trigger("Experiment review"),
                    rx.accordion.content(
                        rx.text(
                            "Capture assumptions, signal quality, and the next hypothesis to test.",
                            size="2",
                            color="gray.9",
                        )
                    ),
                    value="review",
                ),
                rx.accordion.item(
                    rx.accordion.trigger("Ritual upgrade"),
                    rx.accordion.content(
                        rx.text(
                            "Identify one habit that needs a clearer trigger, richer reward, or shorter loop.",
                            size="2",
                            color="gray.9",
                        )
                    ),
                    value="ritual",
                ),
                type="single",
                collapsible=True,
            ),
            gap="4",
            align="start",
        ),
        padding="5",
        width="100%",
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
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.icon("brain", size=28, color="var(--purple-9)"),
                            rx.heading("iMastery Tracker", size="9"),
                            align="center",
                            gap="3",
                        ),
                        rx.spacer(),
                        rx.badge(
                            rx.hstack(
                                rx.icon("activity", size=14),
                                rx.text(
                                    DashboardState.streams_active_count,
                                    weight="medium",
                                ),
                                rx.text("active arcs", size="2"),
                                align="center",
                                gap="2",
                            ),
                            color_scheme="purple",
                            variant="surface",
                        ),
                    ),
                    rx.text(
                        "Design deliberate practice loops, track signals, and celebrate forward motion.",
                        size="3",
                        color="gray.9",
                    ),
                    rx.hstack(
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
                        gap="3",
                        wrap="wrap",
                    ),
                    gap="4",
                    align="start",
                ),
                padding="6",
                width="100%",
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
                    DashboardState.milestone_trend_message,
                    accent="var(--purple-9)",
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
                    accent="var(--amber-9)",
                ),
                metric_card(
                    "radix-icons:activity-log",
                    "Rituals completed",
                    rx.heading(DashboardState.habits_completed_today, size="8", weight="bold"),
                    DashboardState.habit_consistency_copy,
                    accent="var(--cyan-9)",
                ),
                metric_card(
                    "radix-icons:notebook",
                    "Reflection entries",
                    rx.heading(DashboardState.journal_count, size="8", weight="bold"),
                    DashboardState.latest_journal_preview,
                    accent="var(--pink-9)",
                ),
                columns={"base": 1, "md": 2, "lg": 4},
                gap="4",
                width="100%",
            ),
            rx.flex(
                rx.vstack(
                    streams_section(),
                    momentum_insights(),
                    gap="5",
                    width="100%",
                ),
                rx.vstack(
                    habits_section(),
                    journal_section(),
                    practice_playbooks(),
                    gap="5",
                    width="100%",
                ),
                direction={"base": "column", "xl": "row"},
                align="start",
                gap="5",
                width="100%",
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
