"""Saying what the connection is like before packages are downloaded."""

from __future__ import annotations

from nexy.helpers.common.console import console
from nexy.helpers.common.network import Connection, format_speed, quality
from nexy.modules.i18n import t


def _summary(connection: Connection) -> str:
    latency = f"{connection.latency_ms:.0f}"
    if connection.speed_kbps is None:
        return t("init.network.latency", "Connection: {latency} ms").format(latency=latency)
    speed = format_speed(connection.speed_kbps)
    return t("init.network.speed", "Connection: {latency} ms, {speed}").format(
        latency=latency, speed=speed
    )


def _say_offline() -> None:
    offline = t("init.network.offline", "No connection: packages were not installed.")
    hint = t(
        "init.network.offline_hint",
        "When you are online, run uv sync and your package manager's install "
        "in the project folder.",
    )
    console.print(f"[yellow]![/yellow] {offline}")
    console.print(hint)


def is_usable(connection: Connection) -> bool:
    """Say what the connection is; False, with how to install later, when there is none."""
    state = quality(connection)
    if state == "offline":
        _say_offline()
        return False
    console.print(_summary(connection))
    if state == "slow":
        slow = t("init.network.slow", "Slow connection: installing packages may take a while.")
        console.print(f"[yellow]![/yellow] {slow}")
    return True
