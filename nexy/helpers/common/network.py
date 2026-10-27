"""A quick look at the connection, before a step that needs the network.

``nx new`` installs packages; with no connection that waits for timeouts and prints errors, and with
a slow one it looks frozen. The probe tells which case it is in about a second: it times a TCP
connection to the package registries, then downloads a small page to estimate the speed.
"""

from __future__ import annotations

import socket
import time
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

# The registries the installs talk to.
REGISTRIES: tuple[tuple[str, int], ...] = (("pypi.org", 443), ("registry.npmjs.org", 443))
# A page of about a hundred kilobytes: enough to measure, small enough to be quick.
SAMPLE_URL = "https://pypi.org/simple/pip/"
SLOW_LATENCY_MS = 400.0
SLOW_SPEED_KBPS = 100.0
_TIMEOUT = 3.0
_MAX_SAMPLE_BYTES = 400_000


@dataclass(frozen=True)
class Connection:
    online: bool
    latency_ms: float | None
    speed_kbps: float | None


def _connect(host: str, port: int, timeout: float) -> float:
    """Seconds a TCP connection takes; raises OSError when there is none."""
    started = time.perf_counter()
    with socket.create_connection((host, port), timeout=timeout):
        pass
    return time.perf_counter() - started


def _download(url: str, timeout: float) -> tuple[int, float]:
    """Bytes read from `url` and the seconds it took."""
    if not url.startswith("https://"):
        raise ValueError("only https is probed")
    started = time.perf_counter()
    # The URL is a constant of this module, checked to be https above.
    with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec B310
        data = response.read(_MAX_SAMPLE_BYTES)
    return len(data), time.perf_counter() - started


def probe(
    connect: Callable[[str, int, float], float] = _connect,
    download: Callable[[str, float], tuple[int, float]] = _download,
    hosts: tuple[tuple[str, int], ...] = REGISTRIES,
    timeout: float = _TIMEOUT,
) -> Connection:
    """Online or not, how long a connection takes, and roughly how fast a download is."""
    latencies: list[float] = []
    for host, port in hosts:
        try:
            latencies.append(connect(host, port, timeout))
        except OSError:
            continue
    if not latencies:
        return Connection(False, None, None)

    speed: float | None = None
    try:
        size, seconds = download(SAMPLE_URL, timeout)
        if seconds > 0 and size > 0:
            speed = size / 1000 / seconds
    except (OSError, ValueError):
        pass
    return Connection(True, min(latencies) * 1000, speed)


def quality(connection: Connection) -> str:
    """``offline``, ``slow`` or ``good``."""
    if not connection.online:
        return "offline"
    if connection.latency_ms is not None and connection.latency_ms > SLOW_LATENCY_MS:
        return "slow"
    if connection.speed_kbps is not None and connection.speed_kbps < SLOW_SPEED_KBPS:
        return "slow"
    return "good"


def format_speed(kbps: float) -> str:
    """``850 KB/s`` or ``1.5 MB/s``."""
    if kbps >= 1000:
        return f"{kbps / 1000:.1f} MB/s"
    return f"{kbps:.0f} KB/s" if kbps >= 10 else f"{kbps:.1f} KB/s"
