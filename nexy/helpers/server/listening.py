"""What `nx dev` and `nx start` print once the server is ready: where it listens, and how fast."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from nexy.helpers.common import launcher
from nexy.helpers.common.console import console
from nexy.modules.i18n import t

_LOOPBACK = ("127.0.0.1", "localhost")
_ALL_INTERFACES = "0.0.0.0"  # nosec B104 - compared with, never bound to


@dataclass(frozen=True)
class Endpoint:
    """Where the application listens."""

    host: str
    port: int
    ssl_keyfile: str | None = None
    ssl_certfile: str | None = None

    @property
    def protocol(self) -> str:
        return "https" if self.ssl_keyfile and self.ssl_certfile else "http"

    def url(self, host: str) -> str:
        return f"{self.protocol}://{host}:{self.port}"


def print_listening(
    command: str,
    version: str,
    endpoint: Endpoint,
    seconds: float,
    network_ip: Callable[[], str],
) -> None:
    """The header, the addresses (the network one only when it is not loopback), the time."""
    address = network_ip() if endpoint.host == _ALL_INTERFACES else endpoint.host
    launcher.banner(command, version)
    launcher.entry(t("server.local", "Local:"), endpoint.url("localhost"))
    if address not in _LOOPBACK:
        launcher.entry(t("server.network", "Network:"), endpoint.url(address))
    launcher.entry(t("server.ready", "Ready:"), f"{seconds:.2f}s")
    console.print(f"  [dim]{t('server.stop', 'press Ctrl+C to stop')}[/dim]")
