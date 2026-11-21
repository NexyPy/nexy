"""The status card of the hero: what Beacon would show for a small shop. Made up, and fixed, so
the page is the same on every visit."""

from dataclasses import dataclass

DAYS = 45

# Days that were not all up, counted back from today: 0 is today.
_INCIDENTS = {
    "Website": {},
    "API": {31: "slow", 12: "down"},
    "Checkout": {38: "slow"},
    "Webhooks": {22: "down", 21: "slow", 3: "slow"},
}
_HOSTS = {
    "Website": "shop.example",
    "API": "api.shop.example",
    "Checkout": "pay.shop.example",
    "Webhooks": "hooks.shop.example",
}
# What a day of each state costs in uptime, in percent of the day.
_LOST = {"up": 0.0, "slow": 0.0, "down": 1.5}

# Response time over the last 24 hours, one value an hour, in milliseconds.
RESPONSE_MS = [
    182,
    176,
    171,
    169,
    174,
    188,
    205,
    231,
    248,
    236,
    221,
    214,
    209,
    226,
    262,
    241,
    219,
    204,
    198,
    192,
    187,
    181,
    178,
    184,
]


@dataclass(frozen=True)
class Monitor:
    name: str
    host: str
    days: tuple[str, ...]  # oldest first, one state per day: "up", "slow" or "down"

    @property
    def uptime(self) -> str:
        lost = sum(_LOST[state] for state in self.days) / len(self.days)
        return f"{100 - lost:.2f}%"


def monitors() -> list[Monitor]:
    found = []
    for name, incidents in _INCIDENTS.items():
        days = tuple(incidents.get(back, "up") for back in range(DAYS - 1, -1, -1))
        found.append(Monitor(name, _HOSTS[name], days))
    return found


def sparkline(values: list[int], width: int = 240, height: int = 48) -> str:
    """An SVG path through `values`, the highest at the top: the line under the response time."""
    low, high = min(values), max(values)
    spread = high - low or 1
    step = width / (len(values) - 1)
    points = [
        f"{index * step:.1f} {height - (value - low) / spread * height:.1f}"
        for index, value in enumerate(values)
    ]
    return "M" + " L".join(points)


def average(values: list[int]) -> int:
    return round(sum(values) / len(values))
