import reflex as rx


def stream_card(stream: "LearningStream") -> rx.Component:
    """Render a learning stream progress card."""

    # Reflex 0.8+: use rx.cond for all reactive conditions
    progress = rx.cond(
        stream.milestones_total > 0,
        (stream.milestones_completed / stream.milestones_total) * 100,
        0,
    )

    return rx.card(
        rx.vstack(
            # Header bar with total milestones + delete button
            rx.hstack(
                rx.badge(
                    rx.text(f"{stream.milestones_total} planned"),
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
            # Stream title and focus
            rx.heading(stream.name, size="6", weight="bold"),
            rx.text(stream.focus or "", color="gray.9", size="3"),

            # Progress bar
            rx.progress(
                value=progress,
                max=100,
                color_scheme="purple",
                border_radius="lg",
            ),

            # Milestone info and increment/decrement controls
            rx.hstack(
                rx.badge(
                    rx.text(f"{stream.milestones_completed} milestones"),
                    color_scheme="purple",
                ),
                rx.spacer(),
                rx.icon_button(
                    "plus",
                    size="2",
                    variant="solid",
                    color_scheme="purple",
                    on_click=DashboardState.update_stream_progress(stream.id, 1),
                ),
                rx.icon_button(
                    "minus",
                    size="2",
                    variant="soft",
                    color_scheme="purple",
                    on_click=DashboardState.update_stream_progress(stream.id, -1),
                ),
            ),
            gap="3",
            align="start",
            width="100%",
        ),
        # New 0.8+ style: style props are flattened into Chakra-style shorthand
        border_top=f"5px solid {stream.color}",
        padding="5",
        width="100%",
        shadow="sm",
        border_radius="xl",
        transition="all 0.2s ease-in-out",
        _hover={"shadow": "md"},
    )
