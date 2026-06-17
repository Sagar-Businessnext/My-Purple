"""A single, persistent browser Purple drives (Playwright).

By default it launches a headed browser with its own persistent profile, so logins
stick between sessions. Set PURPLE_BROWSER_CDP_URL to instead attach to your own
running Chrome (start it with --remote-debugging-port=9222) and use your real sessions.

The page/context stay alive across tool calls, so Purple keeps a real browsing session.
"""

from __future__ import annotations

import base64
from typing import Any

from purple.config import settings
from purple.utils.logging import get_logger

log = get_logger("browser")


class BrowserController:
    def __init__(self) -> None:
        self._pw: Any | None = None
        self._ctx: Any | None = None
        self._page: Any | None = None

    async def _ensure(self) -> Any:
        if self._page is not None:
            return self._page
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        if settings.browser_cdp_url:
            browser = await self._pw.chromium.connect_over_cdp(settings.browser_cdp_url)
            self._ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        else:
            profile = settings.data_dir / "browser_profile"
            profile.mkdir(parents=True, exist_ok=True)
            self._ctx = await self._pw.chromium.launch_persistent_context(
                user_data_dir=str(profile), headless=settings.browser_headless
            )
        self._page = self._ctx.pages[0] if self._ctx.pages else await self._ctx.new_page()
        log.info("browser_ready", cdp=bool(settings.browser_cdp_url))
        return self._page

    async def goto(self, url: str) -> str:
        page = await self._ensure()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(800)
        return f"{await page.title()} — {page.url}"

    async def read(self, limit: int = 6000) -> str:
        page = await self._ensure()
        return (await page.inner_text("body"))[:limit]

    async def elements(self, limit: int = 40) -> list[dict]:
        page = await self._ensure()
        handles = await page.query_selector_all(
            "a, button, input, textarea, select, [role=button], [role=link]"
        )
        out: list[dict] = []
        for h in handles:
            try:
                if not await h.is_visible():
                    continue
                label = (
                    (await h.inner_text())
                    or (await h.get_attribute("aria-label"))
                    or (await h.get_attribute("placeholder"))
                    or (await h.get_attribute("value"))
                    or ""
                ).strip()
                if not label:
                    continue
                tag = await h.evaluate("e => e.tagName.toLowerCase()")
                out.append({"text": label[:80], "tag": tag})
            except Exception:
                continue
            if len(out) >= limit:
                break
        return out

    async def click_text(self, text: str) -> str:
        page = await self._ensure()
        await page.click(f"text={text}", timeout=8000)
        await page.wait_for_timeout(600)
        return f"clicked '{text}'"

    async def fill(self, selector: str, value: str) -> str:
        page = await self._ensure()
        await page.fill(selector, value, timeout=8000)
        return f"filled {selector}"

    async def press(self, key: str) -> str:
        page = await self._ensure()
        await page.keyboard.press(key)
        await page.wait_for_timeout(600)
        return f"pressed {key}"

    async def back(self) -> str:
        page = await self._ensure()
        await page.go_back()
        return page.url

    async def new_tab(self, url: str | None = None) -> str:
        await self._ensure()
        self._page = await self._ctx.new_page()
        if url:
            return await self.goto(url)
        return "new tab"

    async def list_tabs(self) -> list[str]:
        if self._ctx is None:
            return []
        return [p.url for p in self._ctx.pages]

    async def screenshot_b64(self) -> str | None:
        try:
            page = await self._ensure()
            return base64.b64encode(await page.screenshot()).decode()
        except Exception:
            return None

    async def shutdown(self) -> None:
        try:
            if self._ctx is not None:
                await self._ctx.close()
            if self._pw is not None:
                await self._pw.stop()
        except Exception:
            pass
        self._pw = self._ctx = self._page = None


# Process-wide browser session.
browser = BrowserController()
