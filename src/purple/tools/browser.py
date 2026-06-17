"""Interactive browser tools — Purple drives a real, persistent browser session.

Clicking is commit-guarded: if the link/button text looks like a commit (Pay, Buy,
Place order...), Purple screenshots the page and asks before clicking.
"""

from __future__ import annotations

from purple.browser.controller import browser
from purple.safety import confirm, is_commit_label
from purple.tools.registry import registry

_EMPTY = {"type": "object", "properties": {}, "required": []}
_STR = lambda name: {"type": "object", "properties": {name: {"type": "string"}}, "required": [name]}  # noqa: E731


@registry.tool(
    "browser_open", "Open a URL in Purple's browser (a persistent session).", _STR("url")
)
async def browser_open(url: str) -> str:
    return await browser.goto(url)


@registry.tool("browser_read", "Read the visible text of the current page.", _EMPTY)
async def browser_read() -> str:
    return await browser.read()


@registry.tool(
    "browser_elements",
    "List clickable elements and inputs on the page (text + tag), to decide what to click.",
    _EMPTY,
)
async def browser_elements() -> list[dict] | str:
    els = await browser.elements()
    return els or "no interactive elements found"


@registry.tool(
    "browser_click",
    "Click a link or button by its visible text. Commit-like text (Pay, Buy, Confirm...) "
    "is screenshotted and confirmed first.",
    _STR("text"),
)
async def browser_click(text: str) -> str:
    if is_commit_label(text):
        shot = await browser.screenshot_b64()
        if not await confirm(f"Click '{text}' in the browser?", screenshot_b64=shot):
            return "cancelled — you didn't confirm this commit"
    try:
        return await browser.click_text(text)
    except Exception as exc:
        return f"couldn't click '{text}': {exc}"


@registry.tool(
    "browser_fill",
    'Fill an input field. selector is a CSS selector (e.g. "input[name=\'q\']", "#email").',
    {
        "type": "object",
        "properties": {"selector": {"type": "string"}, "value": {"type": "string"}},
        "required": ["selector", "value"],
    },
)
async def browser_fill(selector: str, value: str) -> str:
    try:
        return await browser.fill(selector, value)
    except Exception as exc:
        return f"couldn't fill {selector}: {exc}"


@registry.tool(
    "browser_press",
    "Press a keyboard key in the browser (e.g. 'Enter', 'Tab').",
    _STR("key"),
)
async def browser_press(key: str) -> str:
    return await browser.press(key)


@registry.tool("browser_back", "Go back to the previous page.", _EMPTY)
async def browser_back() -> str:
    return await browser.back()


@registry.tool(
    "browser_new_tab",
    "Open a new tab, optionally at a URL.",
    {"type": "object", "properties": {"url": {"type": "string"}}, "required": []},
)
async def browser_new_tab(url: str | None = None) -> str:
    return await browser.new_tab(url)


@registry.tool("browser_tabs", "List the URLs of open tabs.", _EMPTY)
async def browser_tabs() -> list[str] | str:
    return await browser.list_tabs() or "no tabs open"


@registry.tool("browser_screenshot", "Screenshot the current page; returns the saved path.", _EMPTY)
async def browser_screenshot() -> str:
    from purple.config import settings

    settings.ensure_dirs()
    path = settings.data_dir / "browser_screen.png"
    page = await browser._ensure()
    await page.screenshot(path=str(path))
    return f"Saved screenshot to {path}"
