"""Human-in-the-loop approval for risky actions.

An 'approver' is an async function (tool_name, args) -> bool. The registry calls it
before running any tool marked requires_confirmation=True. Different front-ends plug
in different approvers: the CLI asks on stdin; the web UI surfaces a confirm dialog.
"""

from __future__ import annotations

import asyncio
from typing import Any


async def console_approver(tool_name: str, args: dict[str, Any]) -> bool:
    """Ask for confirmation on the terminal (used by the CLI / dev mode)."""
    shown = {k: v for k, v in args.items() if not k.endswith("_b64")}
    if any(k.endswith("_b64") for k in args):
        shown["_screenshot"] = "(captured — check your phone screen)"
    prompt = f"\n[CONFIRM] Purple wants to run '{tool_name}' with {shown}\nAllow? [y/N] "
    answer = await asyncio.to_thread(input, prompt)
    return answer.strip().lower() in {"y", "yes"}


async def auto_deny(tool_name: str, args: dict[str, Any]) -> bool:
    """Safe default when no human is available to confirm."""
    return False
