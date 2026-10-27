"""Before installing packages, `nx new` looks at the connection: absent, slow or fine."""

from __future__ import annotations

import pytest

from nexy.helpers.common.network import (
    SLOW_LATENCY_MS,
    SLOW_SPEED_KBPS,
    Connection,
    format_speed,
    probe,
    quality,
)


class Fake:
    """Replaces the two things a probe does on the network."""

    def __init__(self, latencies=None, sample=None, fail_connect=False):
        self.latencies = list(latencies or [])
        self.sample = sample
        self.fail_connect = fail_connect
        self.connected: list[tuple[str, int]] = []

    def connect(self, host: str, port: int, timeout: float) -> float:
        self.connected.append((host, port))
        if self.fail_connect or not self.latencies:
            raise OSError("unreachable")
        return self.latencies.pop(0)

    def download(self, url: str, timeout: float) -> tuple[int, float]:
        if self.sample is None:
            raise OSError("no download")
        return self.sample


def _probe(fake: Fake) -> Connection:
    return probe(
        connect=fake.connect, download=fake.download, hosts=(("a.test", 443), ("b.test", 443))
    )


class TestProbe:
    def test_no_route_to_any_host_means_offline(self):
        result = _probe(Fake(fail_connect=True))
        assert result.online is False and result.latency_ms is None and result.speed_kbps is None

    def test_an_answer_means_online_with_its_latency(self):
        result = _probe(Fake(latencies=[0.040, 0.060], sample=(100_000, 0.5)))
        assert result.online is True
        assert result.latency_ms == pytest.approx(40, abs=1)

    def test_the_fastest_host_is_the_latency(self):
        result = _probe(Fake(latencies=[0.300, 0.050], sample=(100_000, 0.5)))
        assert result.latency_ms == pytest.approx(50, abs=1)

    def test_one_unreachable_host_does_not_make_it_offline(self):
        calls = {"n": 0}

        def connect(host, port, timeout):
            calls["n"] += 1
            if host == "a.test":
                raise OSError("down")
            return 0.020

        result = probe(
            connect=connect,
            download=lambda u, t: (50_000, 0.25),
            hosts=(("a.test", 443), ("b.test", 443)),
        )
        assert result.online is True and calls["n"] == 2

    def test_speed_is_the_sample_size_over_its_time(self):
        result = _probe(Fake(latencies=[0.01, 0.01], sample=(200_000, 1.0)))
        assert result.speed_kbps == pytest.approx(200.0, abs=1)

    def test_a_failed_download_keeps_the_latency_and_has_no_speed(self):
        result = _probe(Fake(latencies=[0.02, 0.02], sample=None))
        assert result.online is True and result.speed_kbps is None

    def test_a_zero_second_download_is_not_a_division_by_zero(self):
        result = _probe(Fake(latencies=[0.02, 0.02], sample=(1000, 0.0)))
        assert result.speed_kbps is None


class TestQuality:
    def test_offline(self):
        assert quality(Connection(False, None, None)) == "offline"

    def test_fast_and_close_is_good(self):
        assert quality(Connection(True, 30.0, 2000.0)) == "good"

    def test_high_latency_is_slow(self):
        assert quality(Connection(True, SLOW_LATENCY_MS + 1, 2000.0)) == "slow"

    def test_low_speed_is_slow(self):
        assert quality(Connection(True, 30.0, SLOW_SPEED_KBPS - 1)) == "slow"

    def test_an_unknown_speed_is_judged_on_latency_alone(self):
        assert quality(Connection(True, 30.0, None)) == "good"
        assert quality(Connection(True, SLOW_LATENCY_MS + 1, None)) == "slow"


class TestFormatSpeed:
    @pytest.mark.parametrize(
        ("kbps", "text"),
        [(0.5, "0.5 KB/s"), (850.0, "850 KB/s"), (1500.0, "1.5 MB/s"), (12_300.0, "12.3 MB/s")],
    )
    def test_it_picks_kilobytes_or_megabytes(self, kbps, text):
        assert format_speed(kbps) == text
