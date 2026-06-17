"""PC control tools (Windows). Launch apps, inspect processes, run commands.

Imports of OS-specific libraries are done lazily inside handlers so this module
imports cleanly on any platform (e.g. when I verify it in a Linux sandbox).
"""

from __future__ import annotations

import asyncio

from purple.tools.registry import registry


@registry.tool(
    name="open_app",
    description="Open or launch an installed application on the user's PC by name, "
    "e.g. 'Steam', 'Wallpaper Engine', 'Spotify', 'Notepad'.",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The application name to launch."}
        },
        "required": ["name"],
    },
)
async def open_app(name: str) -> str:
    def _open() -> str:
        from AppOpener import open as app_open

        app_open(name, match_closest=True, throw_error=True)
        return f"Launched '{name}'."

    return await asyncio.to_thread(_open)


@registry.tool(
    name="list_processes",
    description="List the top running processes by memory use, to see what's open.",
    parameters={
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "How many to return (default 10)."}
        },
        "required": [],
    },
)
async def list_processes(limit: int = 10) -> list[str]:
    def _list() -> list[str]:
        import psutil

        procs = []
        for p in psutil.process_iter(["name", "memory_info"]):
            try:
                mem = p.info["memory_info"].rss / (1024**2)
                procs.append((p.info["name"] or "?", mem))
            except Exception:
                continue
        procs.sort(key=lambda x: x[1], reverse=True)
        return [f"{n} ({m:.0f} MB)" for n, m in procs[:limit]]

    return await asyncio.to_thread(_list)


@registry.tool(
    name="run_command",
    description="Run a shell command on the user's PC. Powerful and potentially "
    "destructive — only for things no other tool covers.",
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The command line to execute."}
        },
        "required": ["command"],
    },
    requires_confirmation=True,  # gated behind the human approver
)
async def run_command(command: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    text = out.decode(errors="replace") if out else ""
    return f"exit={proc.returncode}\n{text[:4000]}"
