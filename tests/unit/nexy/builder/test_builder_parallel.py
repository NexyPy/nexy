import os
import tempfile
from pathlib import Path

from nexy.builder import Builder
from nexy.core.config import Config


def test_builder_thread_pool_runs() -> None:
    builder = Builder()
    result = builder.build(showlog=False)
    assert hasattr(result, "success")
    assert hasattr(result, "failed")
