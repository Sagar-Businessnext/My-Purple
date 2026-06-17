"""Web automation tools via Playwright (read-only in v1).

These let Purple look things up and read pages — e.g. compare flight prices. Actually
committing a purchase would be a separate tool marked requires_confirmation=True so it
always hands the final pay step back to the user.

First-time setup on the PC:  playwright install chromium
"""

from __future__ import annotations

from urllib.parse import quote_plus

from purple.tools.registry import registry

_MAX_TEXT = 6000


async def _read_page(url: str) -> str:
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1500)  # let client-rendered content settle
            text = await page.inner_text("body")
        finally:
            await browser.close()
    return text.strip()


@registry.tool(
    name="web_open_and_read",
    description="Open a web page in a headless browser and return its visible text. "
    "Use for reading articles, prices, schedules, or any client-rendered page.",
    parameters={
        "type": "object",
        "properties": {"url": {"type": "string", "description": "Full https:// URL."}},
        "required": ["url"],
    },
)
async def web_open_and_read(url: str) -> str:
    text = await _read_page(url)
    return text[:_MAX_TEXT]


@registry.tool(
    name="web_search",
    description="Search the web and return the top result snippets for a query.",
    parameters={
        "type": "object",
        "properties": {"query": {"type": "string", "description": "What to search for."}},
        "required": ["query"],
    },
)
async def web_search(query: str) -> str:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    text = await _read_page(url)
    return text[:_MAX_TEXT]
