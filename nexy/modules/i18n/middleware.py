from __future__ import annotations

import http.cookies
import re
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.datastructures import MutableHeaders

from nexy.core.config import Config
from nexy.modules.i18n import L, current_locale


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
        self._cookie_headers: dict[str, str] = {}
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

    def _cookie_from_header(self, raw: bytes | None) -> str | None:
        """The locale cookie's value from a raw ``Cookie`` header, parsed like Starlette does."""
        if raw is None:
            return None
        found: str | None = None
        for chunk in raw.decode("latin-1").split(";"):
            key, sep, value = chunk.partition("=")
            if sep and key.strip() == self._cookie_name:
                found = self._cookie_text(value.strip())
        return found

    def _cookie_text(self, value: str) -> str:
        """A cookie value without its surrounding quotes, decoded by the stdlib parser."""
        if value[:1] != '"':
            return value
        parsed: http.cookies.BaseCookie[str] = http.cookies.SimpleCookie()
        parsed.load(f"{self._cookie_name}={value}")
        morsel = parsed.get(self._cookie_name)
        return morsel.value if morsel is not None else value

    def _detect_from_accept_language(self, raw: bytes | None) -> str | None:
        if raw is None:
            return None
        for part in raw.decode("latin-1").split(","):
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

    def _set_cookie_header(self, locale: str) -> str:
        cached = self._cookie_headers.get(locale)
        if cached is None:
            cached = self._cookie_headers[locale] = self._cookie_value(locale)
        return cached

    @staticmethod
    def _request_headers(headers: list[tuple[bytes, bytes]]) -> tuple[bytes | None, bytes | None]:
        """The ``Cookie`` and ``Accept-Language`` values; repeated headers are joined (RFC 9113)."""
        cookies: list[bytes] = []
        languages: list[bytes] = []
        for name, value in headers:
            if name == b"cookie":
                cookies.append(value)
            elif name == b"accept-language":
                languages.append(value)
        return (b"; ".join(cookies) or None, b", ".join(languages) or None)

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw_cookie, raw_language = self._request_headers(scope["headers"])

        state = scope.setdefault("state", {})
        matched = self._detect_from_url(scope.get("root_path", "") + scope["path"])
        existing = self._cookie_from_header(raw_cookie)

        if matched:
            locale, new_path = matched
            scope["path"] = new_path
            scope["root_path"] = ""
        else:
            locale = (
                (existing if existing in self._available else None)
                or self._detect_from_accept_language(raw_language)
                or self._default
            )

        state["locale"] = locale
        token = current_locale.set(locale)
        try:
            if existing != locale:
                send = self._send_with_cookie(send, self._set_cookie_header(locale))
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
