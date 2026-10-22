from __future__ import annotations

import http.cookies
import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from starlette.datastructures import MutableHeaders

from nexy.core.config import Config
from nexy.i18n import L, current_locale


class LocaleMiddleware:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.config = Config()
        self._init_locales()

    def _init_locales(self) -> None:
        available = self.config.useLocales or L.available_locales()
        default = self.config.useDefaultLocale or "en"
        cookie_name = self.config.useLocaleCookieName or "nexy-locale"
        L.configure(available=available, default=default)
        L._load()
        self._available = available
        self._default = default
        self._cookie_name = cookie_name
        self._prefix_re = re.compile(
            r"^/({})($|/)".format("|".join(re.escape(loc) for loc in available))
        )

    def _detect_from_url(self, path: str) -> tuple[str, str] | None:
        m = self._prefix_re.match(path)
        if m:
            locale = m.group(1)
            rest = path[m.end() :]
            rest = "/" if not rest else "/" + rest
            return locale, rest
        return None

    def _detect_from_cookie(self, request: Request) -> str | None:
        val = request.cookies.get(self._cookie_name)
        if val and val in self._available:
            return val
        return None

    def _detect_from_header(self, request: Request) -> str | None:
        header = request.headers.get("Accept-Language", "")
        for part in header.split(","):
            tag = part.split(";")[0].strip().split("-")[0].lower()
            if tag in self._available:
                return tag
        return None

    def _cookie_value(self, locale: str) -> str:
        cookie: http.cookies.BaseCookie[str] = http.cookies.SimpleCookie()
        cookie[self._cookie_name] = locale
        cookie[self._cookie_name]["max-age"] = 31536000
        cookie[self._cookie_name]["path"] = "/"
        cookie[self._cookie_name]["httponly"] = True
        cookie[self._cookie_name]["samesite"] = "lax"
        return cookie.output(header="").strip()

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        scope.setdefault("state", {})
        matched = self._detect_from_url(request.url.path)

        if matched:
            locale, new_path = matched
            scope["path"] = new_path
            scope["root_path"] = ""
        else:
            locale = (
                self._detect_from_cookie(request)
                or self._detect_from_header(request)
                or self._default
            )

        scope["state"]["locale"] = locale

        existing = request.cookies.get(self._cookie_name)
        token = current_locale.set(locale)
        try:
            if existing != locale:
                cookie_value = self._cookie_value(locale)
                send = self._send_with_cookie(send, cookie_value)
            await self.app(scope, receive, send)
        finally:
            current_locale.reset(token)

    def _send_with_cookie(
        self,
        send: Callable[[dict[str, Any]], Awaitable[None]],
        cookie_value: str,
    ) -> Callable[[dict[str, Any]], Awaitable[None]]:
        async def send_wrapper(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message).append("set-cookie", cookie_value)
            await send(message)

        return send_wrapper
