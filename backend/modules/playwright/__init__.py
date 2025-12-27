import asyncio
from playwright.async_api import async_playwright


import asyncio
import random
import uuid
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
]

VIEWPORTS = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1280, "height": 800},
]

LOCALES = ["en-US", "en-GB", "zh-CN", "ja-JP", "de-DE"]
TIMEZONES = ["Asia/Tokyo", "Europe/London", "America/Los_Angeles", "Asia/Shanghai"]

DEFAULT_HEADERS = {
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua-mobile": "?0",
}


_INIT_SCRIPT = """
// hide webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// languages
Object.defineProperty(navigator, 'languages', { get: () => %s });

// plugins
Object.defineProperty(navigator, 'plugins', { get: () => [{name:'Chrome PDF Plugin'}] });

// chrome object
window.chrome = window.chrome || { runtime: {} };

// hardwareConcurrency and deviceMemory spoof
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => %d });
Object.defineProperty(navigator, 'deviceMemory', { get: () => %d });

// permissions.query spoof (some detectors check this)
const origQuery = window.navigator.permissions && window.navigator.permissions.query;
if (origQuery) {
  window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : origQuery(parameters)
  );
}
"""


class PlaywrightService:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.lock = asyncio.Lock()

    async def start(self):
        async with self.lock:
            if not self.playwright:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=True)

    async def stop(self):
        async with self.lock:
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

    def _random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def _random_viewport(self) -> dict:
        return random.choice(VIEWPORTS)

    def _random_locale(self) -> str:
        return random.choice(LOCALES)

    def _random_timezone(self) -> str:
        return random.choice(TIMEZONES)

    def _random_hardware(self):
        hc = random.choice([2, 4, 8])
        dm = random.choice([4, 8])
        return hc, dm

    async def get_context(
        self,
        *,
        use_new_fingerprint: bool = True,
        proxy: Optional[dict] = None,
        extra_http_headers: Optional[dict] = None,
        user_agent: Optional[str] = None,
    ) -> BrowserContext:
        """
        每次调用返回新 context（默认随机指纹）。
        - use_new_fingerprint=True 每次都会随机化 UA/viewport/locale/timezone/headers/init_script
        - proxy: {'server': 'http://ip:port', 'username': 'u', 'password': 'p'} 如果需要代理
        """
        await self.start()
        if not self.browser:
            raise RuntimeError("browser not started")

        if not use_new_fingerprint:
            ctx = await self.browser.new_context(
                user_agent=user_agent or USER_AGENTS[0],
                extra_http_headers=extra_http_headers or DEFAULT_HEADERS,
            )
            return ctx

        ua = user_agent or self._random_user_agent()
        vp = self._random_viewport()
        locale = self._random_locale()
        tz = self._random_timezone()
        hc, dm = self._random_hardware()

        headers = dict(DEFAULT_HEADERS)
        headers.update(extra_http_headers or {})
        headers["Accept-Language"] = locale
        headers["sec-ch-ua"] = (
            '"Chromium";v="120", "Not=A?Brand";v="24", "Google Chrome";v="120"'
        )

        context_args = {
            "user_agent": ua,
            "viewport": vp,
            "locale": locale,
            "timezone_id": tz,
            "extra_http_headers": headers,
            "ignore_https_errors": True,
        }

        if proxy:
            context_args["proxy"] = proxy

        ctx = await self.browser.new_context(**context_args)

        init_script = _INIT_SCRIPT % (
            str(
                [
                    (
                        locale.split("-")[0] + "-" + locale.split("-")[1]
                        if "-" in locale
                        else locale
                    )
                    for _ in range(1)
                ]
            ),
            hc,
            dm,
        )
        await ctx.add_init_script(init_script)

        fingerprint_tag = str(uuid.uuid4())
        await ctx.add_init_script(f"window.__fingerprint_id = '{fingerprint_tag}';")

        return ctx


_playwright_service: PlaywrightService | None = None


async def init_playwright_service() -> PlaywrightService:
    global _playwright_service
    if _playwright_service is None:
        _playwright_service = PlaywrightService()
        await _playwright_service.start()
    return _playwright_service
