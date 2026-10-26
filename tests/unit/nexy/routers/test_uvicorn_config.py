"""How uvicorn's own log lines look: quiet about startup, labelled, with a traceback if any."""

from __future__ import annotations

import logging
import sys

import pytest

from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG, NexyDefaultFormatter, NexyFilter


def _record(message: str, level: int = logging.INFO, exc_info=None) -> logging.LogRecord:
    return logging.LogRecord("uvicorn.error", level, __file__, 1, message, None, exc_info)


class TestFilter:
    @pytest.mark.parametrize(
        "message",
        [
            "Started server process [1]",
            "Application startup complete.",
            "Uvicorn running on http://0.0.0.0:3000",
            "WebSocket /?token=abc [accepted]",
            "Exception in ASGI application",
            "connection rejected (403 Forbidden)",
        ],
    )
    def test_startup_noise_and_reported_crashes_are_dropped(self, message):
        assert NexyFilter().filter(_record(message)) is False

    def test_a_real_warning_is_kept(self):
        assert NexyFilter().filter(_record("Invalid HTTP request received.")) is True


class TestFormatter:
    def test_a_line_is_the_level_then_an_arrow_then_the_message(self):
        text = NexyDefaultFormatter().format(_record("Port 3000 is busy", logging.ERROR))
        assert text.endswith("» Port 3000 is busy") and "Error" in text

    def test_an_error_is_red_and_the_rest_is_dim(self):
        error = NexyDefaultFormatter().format(_record("x", logging.ERROR))
        info = NexyDefaultFormatter().format(_record("x", logging.INFO))
        assert "\033[31m" in error and "\033[2m" in info

    def test_an_exception_is_followed_by_its_traceback(self):
        try:
            raise ValueError("bad value")
        except ValueError:
            text = NexyDefaultFormatter().format(_record("failed", logging.ERROR, sys.exc_info()))
        assert "Traceback" in text and "ValueError: bad value" in text


def test_the_config_wires_the_filter_and_formatter_to_uvicorn():
    assert set(NEXY_LOG_CONFIG["loggers"]) == {"uvicorn", "uvicorn.error", "uvicorn.access"}
