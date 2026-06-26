from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from nexy.core.config import Config
from nexy.i18n import L, current_locale


class LocaleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any) -> None:
        super().__init__(app)
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
            rest = path[m.end():]
            if not rest:
                rest = "/"
            else:
                rest = "/" + rest
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

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        matched = self._detect_from_url(request.url.path)

        if matched:
            locale, new_path = matched
            request.state.locale = locale
            request.scope["path"] = new_path
            request.scope["root_path"] = ""
            token = current_locale.set(locale)
        else:
            locale = (
                self._detect_from_cookie(request)
                or self._detect_from_header(request)
                or self._default
            )
            request.state.locale = locale
            token = current_locale.set(locale)

        try:
            response = await call_next(request)
            existing = request.cookies.get(self._cookie_name)
            if existing != locale:
                response.set_cookie(
                    key=self._cookie_name,
                    value=locale,
                    max_age=31536000,
                    httponly=True,
                    samesite="lax",
                )
            return response
        finally:
            current_locale.reset(token)
