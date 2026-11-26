"""ISR stores share one rendered page per URL across memory, disk and Redis."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from nexy.core.config import Config
from nexy.modules.runtime import cache as cache_module
from nexy.modules.runtime.cache import (
    CacheEntry,
    FileISRCache,
    ISRCache,
    RedisISRCache,
    RevalidateCache,
    get_isr_cache,
    reset_isr_cache,
)


class FakeRedis:
    """The subset of a Redis client the ISR store uses."""

    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    def get(self, key: str) -> bytes | None:
        return self.values.get(key)

    def set(self, key: str, value: str | bytes) -> None:
        self.values[key] = value.encode("utf-8") if isinstance(value, str) else value

    def delete(self, *keys: str) -> None:
        for key in keys:
            self.values.pop(key, None)

    def scan_iter(self, match: str) -> list[str]:
        prefix = match.removesuffix("*")
        return [key for key in self.values if key.startswith(prefix)]


class CustomCache:
    def get(self, _path: str) -> CacheEntry | None:
        return None

    def set(self, _path: str, _value: str, _revalidate: int | None = None) -> None:
        return None

    def invalidate(self, _path: str) -> None:
        return None


@pytest.fixture(autouse=True)
def _fresh_resolver() -> Any:
    reset_isr_cache()
    yield
    reset_isr_cache()


@pytest.fixture
def fixed_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cache_module.time, "time", lambda: 1000.0)


@pytest.fixture
def fake_redis_import(monkeypatch: pytest.MonkeyPatch) -> None:
    class RedisModule:
        @staticmethod
        def from_url(_url: str) -> FakeRedis:
            return FakeRedis()

    monkeypatch.setattr(
        cache_module.importlib,
        "import_module",
        lambda _name: SimpleNamespace(Redis=RedisModule),
    )


class TestMemoryStore:
    def test_the_memory_store_satisfies_the_protocol(self):
        assert isinstance(RevalidateCache(), ISRCache)

    def test_invalidate_removes_one_path(self):
        cache = RevalidateCache()
        cache.set("/blog", "body", 60)
        cache.set("/about", "body", 60)
        cache.invalidate("/blog")
        assert cache.get("/blog") is None

    def test_invalidate_keeps_other_paths(self):
        cache = RevalidateCache()
        cache.set("/blog", "body", 60)
        cache.set("/about", "body", 60)
        cache.invalidate("/blog")
        assert cache.get("/about") is not None

    def test_invalidate_all_clears_the_store(self):
        cache = RevalidateCache()
        cache.set("/blog", "body", 60)
        cache.invalidate("*")
        assert cache.get("/blog") is None


@pytest.mark.usefixtures("fixed_clock")
class TestFileStore:
    def test_two_instances_share_one_entry(self, tmp_path: Path):
        writer = FileISRCache(tmp_path)
        reader = FileISRCache(tmp_path)
        writer.set("/blog", "<h1>Hello</h1>", 60)
        assert reader.get("/blog") == CacheEntry("<h1>Hello</h1>", 1060.0, 60)

    def test_the_expiry_is_written_to_disk(self, tmp_path: Path):
        cache = FileISRCache(tmp_path)
        cache.set("/blog", "body", 60)
        payload = json.loads((tmp_path / f"{cache_module._path_key('/blog')}.json").read_text())
        assert payload == {"value": "body", "expires_at": 1060.0, "revalidate": 60}

    @pytest.mark.parametrize("window", [None, 0, -1])
    def test_a_page_without_a_window_is_not_stored(self, tmp_path: Path, window: int | None):
        cache = FileISRCache(tmp_path)
        cache.set("/blog", "body", window)
        assert cache.get("/blog") is None

    def test_invalidate_removes_one_path(self, tmp_path: Path):
        cache = FileISRCache(tmp_path)
        cache.set("/blog", "body", 60)
        cache.invalidate("/blog")
        assert cache.get("/blog") is None

    def test_invalidate_all_clears_the_directory(self, tmp_path: Path):
        cache = FileISRCache(tmp_path)
        cache.set("/blog", "body", 60)
        cache.set("/about", "body", 60)
        cache.invalidate("*")
        assert (cache.get("/blog"), cache.get("/about")) == (None, None)

    def test_a_corrupt_file_is_a_miss(self, tmp_path: Path):
        path = tmp_path / f"{cache_module._path_key('/blog')}.json"
        path.write_text("not json")
        assert FileISRCache(tmp_path).get("/blog") is None

    def test_a_missing_directory_is_a_miss(self, tmp_path: Path):
        assert FileISRCache(tmp_path / "absent").get("/blog") is None

    def test_set_replaces_the_previous_body(self, tmp_path: Path):
        cache = FileISRCache(tmp_path)
        cache.set("/blog", "first", 60)
        cache.set("/blog", "second", 60)
        assert cache.get("/blog") == CacheEntry("second", 1060.0, 60)

    def test_a_failed_write_leaves_no_temporary_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        def refuse(*_args: Any) -> None:
            raise OSError("disk full")

        monkeypatch.setattr(cache_module.os, "replace", refuse)
        with pytest.raises(OSError):
            FileISRCache(tmp_path).set("/blog", "body", 60)
        assert list(tmp_path.glob(".tmp-*")) == []


@pytest.mark.usefixtures("fixed_clock")
class TestRedisStore:
    def test_the_store_reads_a_shared_entry(self):
        client = FakeRedis()
        cache = RedisISRCache(client)
        cache.set("/blog", "<h1>Hello</h1>", 60)
        assert cache.get("/blog") == CacheEntry("<h1>Hello</h1>", 1060.0, 60)

    @pytest.mark.parametrize("window", [None, 0, -1])
    def test_a_page_without_a_window_is_not_stored(self, window: int | None):
        cache = RedisISRCache(FakeRedis())
        cache.set("/blog", "body", window)
        assert cache.get("/blog") is None

    def test_invalidate_removes_one_path(self):
        client = FakeRedis()
        cache = RedisISRCache(client)
        cache.set("/blog", "body", 60)
        cache.invalidate("/blog")
        assert cache.get("/blog") is None

    def test_invalidate_all_removes_only_nexy_keys(self):
        client = FakeRedis()
        client.set("another:key", "keep")
        cache = RedisISRCache(client)
        cache.set("/blog", "body", 60)
        cache.set("/about", "body", 60)
        cache.invalidate("*")
        assert client.values == {"another:key": b"keep"}

    def test_a_corrupt_payload_is_a_miss(self):
        client = FakeRedis()
        client.set(cache_module._redis_key("/blog"), "not json")
        assert RedisISRCache(client).get("/blog") is None

    def test_a_payload_without_the_body_is_a_miss(self):
        client = FakeRedis()
        client.set(cache_module._redis_key("/blog"), json.dumps({"expires_at": 1060.0}))
        assert RedisISRCache(client).get("/blog") is None

    def test_an_undecodable_payload_is_a_miss(self):
        client = FakeRedis()
        client.set(cache_module._redis_key("/blog"), b"\xff")
        assert RedisISRCache(client).get("/blog") is None


class TestStoreSelection:
    def test_the_default_is_the_shared_memory_store(self):
        Config()
        assert get_isr_cache() is cache_module.REVALIDATE_CACHE

    def test_the_same_selection_reuses_one_store(self):
        Config()
        assert get_isr_cache() is get_isr_cache()

    @pytest.mark.usefixtures("fake_redis_import")
    @pytest.mark.parametrize("name", ["memory", "file", "redis"])
    def test_a_name_selects_the_store(self, monkeypatch: pytest.MonkeyPatch, name: str):
        Config()
        monkeypatch.setattr(Config, "useISRCache", name)
        kinds = {"memory": RevalidateCache, "file": FileISRCache, "redis": RedisISRCache}
        assert isinstance(get_isr_cache(), kinds[name])

    def test_a_file_mapping_takes_its_directory(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        Config()
        monkeypatch.setattr(Config, "useISRCache", {"type": "file", "directory": str(tmp_path)})
        assert get_isr_cache().directory == tmp_path

    def test_a_redis_mapping_can_take_a_client(self, monkeypatch: pytest.MonkeyPatch):
        Config()
        client = FakeRedis()
        monkeypatch.setattr(Config, "useISRCache", {"type": "redis", "client": client})
        assert get_isr_cache().client is client

    def test_a_redis_mapping_reads_the_url(self, monkeypatch: pytest.MonkeyPatch):
        Config()
        seen: list[str] = []

        class RedisModule:
            @staticmethod
            def from_url(url: str) -> FakeRedis:
                seen.append(url)
                return FakeRedis()

        monkeypatch.setattr(
            cache_module.importlib,
            "import_module",
            lambda _name: SimpleNamespace(Redis=RedisModule),
        )
        monkeypatch.setattr(
            Config, "useISRCache", {"type": "redis", "url": "redis://cache.test:6379/2"}
        )
        get_isr_cache()
        assert seen == ["redis://cache.test:6379/2"]

    def test_a_missing_redis_package_names_the_command(self, monkeypatch: pytest.MonkeyPatch):
        Config()
        monkeypatch.setattr(
            cache_module.importlib,
            "import_module",
            lambda name: (_ for _ in ()).throw(ModuleNotFoundError(name)),
        )
        monkeypatch.setattr(Config, "useISRCache", {"type": "redis"})
        with pytest.raises(RuntimeError, match="uv add redis"):
            get_isr_cache()

    def test_a_custom_store_is_used_as_it_is(self, monkeypatch: pytest.MonkeyPatch):
        Config()
        custom = CustomCache()
        monkeypatch.setattr(Config, "useISRCache", custom)
        assert get_isr_cache() is custom

    @pytest.mark.parametrize("spec", ["disk", {"type": "disk"}, {"directory": ".nexy/isr"}, 42])
    def test_an_unknown_selection_is_refused(self, monkeypatch: pytest.MonkeyPatch, spec: Any):
        Config()
        monkeypatch.setattr(Config, "useISRCache", spec)
        with pytest.raises(ValueError, match="ISR cache"):
            get_isr_cache()
