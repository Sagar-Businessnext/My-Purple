"""Tool package. Importing it registers all built-in tools onto the shared registry."""

from purple.tools.registry import registry


def load_tools() -> None:
    """Import tool modules for their registration side-effects. Call once at startup."""
    from purple.tools import (
        automations,  # noqa: F401
        briefing,  # noqa: F401
        browser,  # noqa: F401
        desktop_ui,  # noqa: F401
        documents,  # noqa: F401
        email_calendar,  # noqa: F401
        files,  # noqa: F401
        memory_tools,  # noqa: F401
        missions,  # noqa: F401
        observe,  # noqa: F401
        phone,  # noqa: F401
        productivity,  # noqa: F401
        smarthome,  # noqa: F401
        system_control,  # noqa: F401
        system_pc,  # noqa: F401
        vision,  # noqa: F401
        web_automation,  # noqa: F401
    )


__all__ = ["load_tools", "registry"]
