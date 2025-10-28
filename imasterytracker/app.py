from __future__ import annotations

import reflex as rx

from .state import DashboardState, Habit, JournalEntry, LearningStream


def section_header(title: str, description: str) -> rx.Component:
    """Reusable page section header."""

    return rx.vstack(
        rx.heading(title, size="7", weight="bold"),
        rx.text(description, color="gray.10", size="3"),
        align="start",
        gap="1",
        width="100%",
    )


def stat_card(title: str, metric: rx.Component, copy: rx.Component) -> rx.Component:
    """Render a highlight statistic card."""

    return rx.card(
        rx.vstack(
            rx.text(title.upper(), size="2", letter_spacing="0.2em", color="gray.9"),
            metric,
            copy,
            align="start",
            gap="2",
            width="100%",
        ),
        width="100%",
        padding="6",
        border_radius="2xl",
        shadow="sm",
    )


def hero_section() -> rx.Component:
    """Top hero copy introducing the dashboard."""

    return rx.vstack(
        rx.text("iMasteryTracker", size="9", weight="bold"),
        rx.text(
            "Design deliberate practice loops, capture insights, and track the rituals that keep momentum steady.",
            size="4",
            max_width="820px",
            color="gray.10",
        ),
        rx.hstack(
            rx.badge(DashboardState.next_stream_message, color_scheme="purple"),
            rx.badge(DashboardState.habit_consistency_copy, color_scheme="green"),
            rx.badge(DashboardState.latest_journal_preview, color_scheme="orange"),
            spacing="3",
            wrap="wrap",
            width="100%",
        ),
        align="start",
        gap="4",
        width="100%",
    )


def stats_section() -> rx.Component:
    """Key stats for the dashboard."""

    return rx.grid(
        stat_card(
            "Milestones shipped",
            rx.hstack(
                rx.heading(DashboardState.milestone_completion, size="8"),
                rx.text("%", size="4", color="gray.9"),
                align="baseline",
            ),
            rx.text(DashboardState.milestone_trend_message, color="gray.10", size="3"),
        ),
        stat_card(
            "Practice arcs",
            rx.heading(DashboardState.total_streams, size="8"),
            rx.text(DashboardState.milestone_detail, color="gray.10", size="3"),
        ),
        stat_card(
            "Ritual cadence",
            rx.hstack(
                rx.heading(DashboardState.habits_completed_today, size="8"),
                rx.text("today", size="4", color="gray.9"),
                align="baseline",
            ),
            rx.text(DashboardState.habit_consistency_copy, color="gray.10", size="3"),
        ),
        columns=rx.breakpoints(initial="1", md="3"),
        gap="5",
        width="100%",
    )


def stream_card(stream: LearningStream) -> rx.Component:
    """Render a learning stream progress card."""

    progress = rx.cond(
        stream.milestones_total > 0,
        (stream.milestones_completed / stream.milestones_total) * 100,
        0,
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.hstack(
                        rx.text(stream.milestones_total, font_weight="semibold"),
                        rx.text("planned", color="gray.9"),
                        spacing="1",
                        align="center",
                    ),
                    color_scheme="gray",
                ),
                rx.spacer(),
                rx.icon_button(
                    "trash-2",
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=DashboardState.remove_stream(stream.id),
                ),
            ),
            rx.heading(stream.name, size="6", weight="bold"),
            rx.text(stream.focus, color="gray.9", size="3"),
            rx.progress(
                value=progress,
                max=100,
                color_scheme="purple",
                border_radius="lg",
            ),
            rx.hstack(
                rx.badge(
                    rx.hstack(
                        rx.text(stream.milestones_completed, font_weight="semibold"),
                        rx.text("milestones", color="gray.9"),
                        spacing="1",
                        align="center",
                    ),
                    color_scheme="purple",
                ),
                rx.spacer(),
                rx.icon_button(
                    "plus",
                    size="2",
                    variant="soft",
                    color_scheme="purple",
                    on_click=DashboardState.update_stream_progress(stream.id, 1),
                ),
                rx.icon_button(
                    "minus",
                    size="2",
                    variant="solid",
                    color_scheme="purple",
                    on_click=DashboardState.update_stream_progress(stream.id, -1),
                ),
            ),
            gap="4",
            align="start",
            width="100%",
        ),
        border_top_width="5px",
        border_top_style="solid",
        border_top_color=stream.color,
        padding="5",
        width="100%",
        shadow="sm",
        border_radius="xl",
        transition="all 0.2s ease-in-out",
        _hover={"shadow": "md"},
    )


def stream_modal() -> rx.Component:
    """Inline modal for creating a new learning stream."""

    return rx.card(
        rx.vstack(
            rx.heading("New learning stream", size="5"),
            rx.text(
                "Set the focus and milestone plan for a new arc of deliberate practice.",
                color="gray.10",
            ),
            rx.input(
                placeholder="Stream name",
                value=DashboardState.stream_name,
                on_change=DashboardState.set_stream_name,
            ),
            rx.text_area(
                placeholder="What are you focusing on?",
                value=DashboardState.stream_focus,
                on_change=DashboardState.set_stream_focus,
                min_height="120px",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Planned milestones",
                    type="number",
                    value=DashboardState.stream_milestones_total,
                    on_change=DashboardState.set_stream_milestones_total,
                ),
                rx.input(
                    placeholder="Completed",
                    type="number",
                    value=DashboardState.stream_milestones_completed,
                    on_change=DashboardState.set_stream_milestones_completed,
                ),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="gray",
                    on_click=DashboardState.close_stream_modal,
                ),
                rx.spacer(),
                rx.button(
                    "Create stream",
                    color_scheme="purple",
                    on_click=DashboardState.add_stream,
                ),
                width="100%",
            ),
            gap="4",
            width="100%",
            align="start",
        ),
        width="100%",
        padding="6",
        border_radius="2xl",
        shadow="md",
        background_color="rgba(255, 255, 255, 0.04)",
    )


def streams_section() -> rx.Component:
    """Section showing all learning streams."""

    return rx.vstack(
        section_header(
            "Learning streams",
            "Track the long arcs of mastery and make deliberate practice visible.",
        ),
        rx.hstack(
            rx.button(
                "New stream",
                on_click=DashboardState.open_stream_modal,
                color_scheme="purple",
            ),
            rx.spacer(),
            rx.text(DashboardState.milestone_copy, color="gray.10", size="3"),
            width="100%",
        ),
        rx.cond(
            DashboardState.total_streams > 0,
            rx.grid(
                rx.foreach(DashboardState.streams, stream_card),
                columns= rx.breakpoints(initial="1", md="2"),
                spacing="4",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("No streams yet", size="5"),
                    rx.text(
                        "Capture your first focus area to start charting progress.",
                        color="gray.10",
                    ),
                    align="start",
                    gap="2",
                    width="100%",
                ),
                width="100%",
                padding="6",
                border_radius="2xl",
            ),
        ),
        rx.cond(
            DashboardState.show_stream_modal,
            stream_modal(),
            rx.fragment(),
        ),
        gap="5",
        width="100%",
    )


def habit_card(habit: Habit) -> rx.Component:
    """Render an individual habit card."""

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(habit.name, size="5"),
                rx.badge(habit.cadence, color_scheme="green"),
                rx.spacer(),
                rx.icon_button(
                    "trash-2",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=DashboardState.remove_habit(habit.id),
                ),
            ),
            rx.text(habit.context, color="gray.9", size="3"),
            rx.hstack(
            rx.cond(
                habit.last_completed_on,
                rx.text(habit.last_completed_on, color="gray.10", size="3"),
                rx.text("Not logged yet", color="gray.10", size="3"),
            ),
                rx.spacer(),
                rx.button(
                    "Log today",
                    size="2",
                    variant="solid",
                    color_scheme="green",
                    on_click=DashboardState.toggle_habit(habit.id),
                ),
            ),
            gap="3",
            align="start",
            width="100%",
        ),
        width="100%",
        padding="5",
        border_radius="xl",
    )


def habit_modal() -> rx.Component:
    """Inline modal form for adding a new habit."""

    return rx.card(
        rx.vstack(
            rx.heading("New ritual", size="5"),
            rx.text("Log a recurring habit that reinforces your practice rhythm.", color="gray.10"),
            rx.input(
                placeholder="Habit name",
                value=DashboardState.habit_name,
                on_change=DashboardState.set_habit_name,
            ),
            rx.input(
                placeholder="Cadence",
                value=DashboardState.habit_cadence,
                on_change=DashboardState.set_habit_cadence,
            ),
            rx.text_area(
                placeholder="Context or why it matters",
                value=DashboardState.habit_context,
                on_change=DashboardState.set_habit_context,
                min_height="120px",
            ),
            rx.hstack(
                rx.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="gray",
                    on_click=DashboardState.close_habit_modal,
                ),
                rx.spacer(),
                rx.button(
                    "Save habit",
                    color_scheme="green",
                    on_click=DashboardState.add_habit,
                ),
                width="100%",
            ),
            gap="4",
            align="start",
            width="100%",
        ),
        width="100%",
        padding="6",
        border_radius="2xl",
        shadow="md",
        background_color="rgba(255, 255, 255, 0.04)",
    )


def habits_section() -> rx.Component:
    """Section listing rituals and habits."""

    return rx.vstack(
        section_header(
            "Ritual cadence",
            "Daily and weekly practices that keep momentum steady.",
        ),
        rx.hstack(
            rx.button(
                "New ritual",
                on_click=DashboardState.open_habit_modal,
                color_scheme="green",
            ),
            rx.spacer(),
            rx.text(DashboardState.habit_consistency_copy, color="gray.10", size="3"),
            width="100%",
        ),
        rx.cond(
            DashboardState.total_habits > 0,
            rx.simple_grid(
                rx.foreach(DashboardState.habits, habit_card),
                columns=[1, 1, 2],
                spacing="4",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("No rituals yet", size="5"),
                    rx.text(
                        "Document the keystone habits that make progress inevitable.",
                        color="gray.10",
                    ),
                    align="start",
                    gap="2",
                    width="100%",
                ),
                width="100%",
                padding="6",
                border_radius="2xl",
            ),
        ),
        rx.cond(
            DashboardState.show_habit_modal,
            habit_modal(),
            rx.fragment(),
        ),
        gap="5",
        width="100%",
    )


def journal_card(entry: JournalEntry) -> rx.Component:
    """Render a single journal entry card."""

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(entry.title, size="5"),
                rx.spacer(),
                rx.badge(entry.mood, color_scheme="orange"),
                rx.icon_button(
                    "trash-2",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=DashboardState.remove_journal_entry(entry.id),
                ),
            ),
            rx.text(entry.reflection, color="gray.10", size="3"),
            rx.text(entry.created_at, color="gray.8", size="2"),
            gap="3",
            align="start",
            width="100%",
        ),
        width="100%",
        padding="5",
        border_radius="xl",
    )


def journal_modal() -> rx.Component:
    """Inline modal for capturing a new reflection."""

    return rx.card(
        rx.vstack(
            rx.heading("New reflection", size="5"),
            rx.text("Capture the insight that moved the needle today.", color="gray.10"),
            rx.input(
                placeholder="Entry title",
                value=DashboardState.journal_title,
                on_change=DashboardState.set_journal_title,
            ),
            rx.text_area(
                placeholder="What did you learn, synthesise, or decide?",
                value=DashboardState.journal_reflection,
                on_change=DashboardState.set_journal_reflection,
                min_height="140px",
            ),
            rx.input(
                placeholder="Mood",
                value=DashboardState.journal_mood,
                on_change=DashboardState.set_journal_mood,
            ),
            rx.hstack(
                rx.button(
                    "Cancel",
                    variant="soft",
                    color_scheme="gray",
                    on_click=DashboardState.close_journal_modal,
                ),
                rx.spacer(),
                rx.button(
                    "Save reflection",
                    color_scheme="orange",
                    on_click=DashboardState.add_journal_entry,
                ),
                width="100%",
            ),
            gap="4",
            align="start",
            width="100%",
        ),
        width="100%",
        padding="6",
        border_radius="2xl",
        shadow="md",
        background_color="rgba(255, 255, 255, 0.04)",
    )


def journal_section() -> rx.Component:
    """Section containing journal entries."""

    return rx.vstack(
        section_header(
            "Mastery journal",
            "Document breakthroughs and signal where to iterate next.",
        ),
        rx.hstack(
            rx.button(
                "New reflection",
                on_click=DashboardState.open_journal_modal,
                color_scheme="orange",
            ),
            rx.spacer(),
            rx.cond(
                DashboardState.journal_count > 0,
                rx.hstack(
                    rx.heading(DashboardState.journal_count, size="5"),
                    rx.text("entries logged", color="gray.10", size="3"),
                    align="baseline",
                ),
                rx.text("No reflections logged", color="gray.10", size="3"),
            ),
            width="100%",
        ),
        rx.cond(
            DashboardState.journal_count > 0,
            rx.vstack(
                rx.foreach(DashboardState.journal_entries, journal_card),
                gap="4",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("No reflections yet", size="5"),
                    rx.text(
                        "Capture your latest insight to build your mastery journal.",
                        color="gray.10",
                    ),
                    align="start",
                    gap="2",
                    width="100%",
                ),
                width="100%",
                padding="6",
                border_radius="2xl",
            ),
        ),
        rx.cond(
            DashboardState.show_journal_modal,
            journal_modal(),
            rx.fragment(),
        ),
        gap="5",
        width="100%",
    )


def toast_banner() -> rx.Component:
    """Banner showing the latest toast message."""

    return rx.cond(
        DashboardState.toast_message != "",
        rx.card(
            rx.hstack(
                rx.text(DashboardState.toast_message, size="3"),
                rx.spacer(),
                rx.icon_button(
                    "x",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=DashboardState.clear_toast,
                ),
            ),
            width="100%",
            padding="4",
            border_radius="lg",
            background_color="rgba(255, 255, 255, 0.06)",
        ),
        rx.fragment(),
    )


@rx.page(route="/", title="iMasteryTracker")
def index() -> rx.Component:
    """Primary dashboard page."""

    return rx.box(
        rx.center(
            rx.vstack(
                hero_section(),
                toast_banner(),
                stats_section(),
                streams_section(),
                habits_section(),
                journal_section(),
                gap="10",
                width="100%",
                max_width="1100px",
            ),
            padding_x="6",
            padding_y="10",
        ),
        width="100%",
    )


app = rx.App(_state=DashboardState)
app.add_page(index)
