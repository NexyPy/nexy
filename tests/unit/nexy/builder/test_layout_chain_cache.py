import tempfile
from pathlib import Path

from nexy.builder import _get_layout_chain, _layout_chain_cache


def test_layout_chain_memoizes_per_directory() -> None:
    _layout_chain_cache.clear()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        chain = _get_layout_chain(root)
        assert root.as_posix() in _layout_chain_cache
        assert _layout_chain_cache[root.as_posix()] == chain


def test_layout_chain_returns_cached_value() -> None:
    _layout_chain_cache.clear()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _layout_chain_cache[root.as_posix()] = "cached"
        assert _get_layout_chain(root) == "cached"
